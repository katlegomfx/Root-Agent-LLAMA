import sys
import os
import time
import json
import threading
import subprocess
import itertools
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional

# Add core to sys.path to ensure imports work
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.context_agent import ContextAgent

# --- CONFIGURATION ---
MODEL_NAME = "gemma3:4b"
OLLAMA_URL = "http://localhost:11434/api/chat"

# --- UTILS ---

class Spinner:
    """A simple spinner for CLI feedback."""
    def __init__(self, message="Processing..."):
        self.message = message
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()

    def _spin(self):
        while self.running:
            sys.stdout.write(f'\r{self.message} {next(self.spinner)}')
            sys.stdout.flush()
            time.sleep(0.1)

class TaskManager:
    """Interface for the improvements_manager.py script."""
    def __init__(self, script_path: str, project_root: str):
        self.script_path = script_path
        self.project_root = project_root
        self.db_path = Path(project_root) / "improvements.json"
        
        # Auto-init if needed
        if not self.db_path.exists():
            self._run("init", self.project_root)

    def _run(self, *args) -> str:
        cmd = [sys.executable, self.script_path] + list(args)
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            return res.stdout.strip()
        except Exception as e:
            return f"Error running improvements manager: {e}"

    def list_tasks(self, status=None, search=None):
        args = ["list"]
        if status: args.extend(["--status", status])
        if search: args.extend(["--search", search])
        return self._run(*args)
    
    def add_task(self, title):
        return self._run("add", title)
        
    def pick_next(self):
        return self._run("next")
        
    def resolve_current(self):
        return self._run("resolve")
    
    def scan(self):
        return self._run("scan")

    def get_progress_summary(self):
        output = self.list_tasks(status="in_progress")
        if "in_progress" in output:
            return f"Current Tracked Improvement:\n{output}\n"
        return "No specific task currently tracked in improvements_manager."

class IOManager:
    """Handles low-level process IO and buffer management."""
    def __init__(self, command: List[str]):
        self.command = command
        self.process = None
        self.stdout_buffer = []
        self._buffer_lock = threading.Lock()
        self._stop_event = threading.Event()
        self.thread = None

    def start(self):
        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        try:
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.getcwd(),
                env=env
            )
            self.thread = threading.Thread(target=self._reader, daemon=True)
            self.thread.start()
            print(f"[IO] Started process: {' '.join(self.command)}")
        except Exception as e:
            print(f"[IO] Failed to start process: {e}")
            raise

    def _reader(self):
        while not self._stop_event.is_set():
            if not self.process:
                break
            
            if self.process.poll() is not None:
                remainder = self.process.stdout.read()
                if remainder:
                     sys.stdout.write(remainder)
                     with self._buffer_lock:
                        self.stdout_buffer.extend(list(remainder))
                break

            try:
                char = self.process.stdout.read(1)
            except ValueError:
                break

            if not char:
                break
            
            sys.stdout.write(char) 
            sys.stdout.flush()
            
            with self._buffer_lock:
                self.stdout_buffer.append(char)

    def get_snapshot(self, last_chars: int = 2000) -> str:
        with self._buffer_lock:
            full_text = "".join(self.stdout_buffer)
        return full_text[-last_chars:] if len(full_text) > last_chars else full_text

    def send_input(self, text: str):
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(text + "\n")
                self.process.stdin.flush()
            except Exception as e:
                print(f"[IO] Error sending input: {e}")

    def cleanup(self):
        self._stop_event.set()
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        print("\n[IO] Process cleaned up.")


class MetaBrain:
    """Handles prompt loading and LLM Inference."""
    def __init__(self, model: str = MODEL_NAME):
        self.model = model
        self.prompts_dir = Path("prompts")

    def _load_prompt(self, filename: str) -> str:
        try:
            # Check local 'prompts' folder
            p = self.prompts_dir / filename
            if p.exists():
                return p.read_text(encoding="utf-8")
        except Exception:
            pass
        return ""

    def query_ollama(self, messages: List[Dict], system_prompt: str = None, model: str = None) -> str:
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        use_model = model if model else self.model
        
        data = {
            "model": use_model,
            "messages": messages,
            "stream": False
        }
        
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            # Removed timeout as requested by user
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("message", {}).get("content", "")
        except Exception as e:
            print(f"[Brain] Inference Error: {e}")
            return ""

    def decide_next_action(self, state_snapshot: str, goal: str, history: List[Dict], progress_summary: str = "N/A") -> Dict:
        template = self._load_prompt("meta_prompt.md")
        if not template:
            return {"confidence": "low", "error": "Prompt missing"}

        filled_prompt = template.format(
            stdout_snapshot=state_snapshot,
            user_goal=goal,
            progress_summary=progress_summary,
            recent_conversation=json.dumps(history[-3:], indent=2)
        )

        response = self.query_ollama([{"role": "user", "content": filled_prompt}])
        
        try:
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            json_str = json_match.group(1) if json_match else response
            return json.loads(json_str)
        except:
            print(f"[Brain] Failed to parse JSON decisions: {response[:100]}...")
            return {"action": "wait", "confidence": "low"}


# --- CORE ORCHESTRATOR ---

class Orchestrator:
    def __init__(self, gui_script_path: str):
        self.cli = IOManager([sys.executable, gui_script_path])
        self.brain = MetaBrain()
        
        # Paths
        script_dir = Path(__file__).parent
        self.project_root = script_dir
        
        repl_path = self.project_root / "core" / "rlm_repl.py"
        imp_script = self.project_root / "core" / "improvements_manager.py"
        
        self.tasks = TaskManager(str(imp_script), str(self.project_root))
        
        inference_adapter = self.brain.query_ollama
        self.subagent = ContextAgent(inference_adapter, str(repl_path))
        self.history = []

    def run_goal(self, user_goal: str):
        print(f"\n{'='*50}\nSTARTING GOAL: {user_goal}\n{'='*50}")
        
        try:
            self.cli.start()
            time.sleep(1)

            max_steps = 20
            for i in range(max_steps):
                print(f"\n[Loop {i+1}] Observing...")
                
                snapshot = self.cli.get_snapshot()
                progress = self.tasks.get_progress_summary()
                
                spinner = Spinner("Thinking...")
                spinner.start()
                try:
                    decision = self.brain.decide_next_action(
                        state_snapshot=snapshot,
                        goal=user_goal,
                        history=self.history,
                        progress_summary=progress
                    )
                finally:
                    spinner.stop()
                
                action = decision.get("action", "cli_interaction")
                confidence = decision.get("confidence", "low")
                print(f"[Decision] {action} (Conf: {confidence})")

                if action == 'delegate_to_subagent':
                    task = decision.get("subagent_task", "Analyze situation")
                    print(f"[Action] Delegating to Subagent: {task}")
                    
                    spinner = Spinner("Subagent working...")
                    spinner.start()
                    try:
                        result = self.subagent.execute_task(task)
                    finally:
                        spinner.stop()
                    
                    self.history.append({
                        "role": "system",
                        "content": f"Subagent Output: {result}"
                    })
                    print(f"[Result] {result[:100]}...")

                elif action == 'cli_interaction':
                    sys_p = decision.get("system_prompt", "You are a CLI operator.")
                    user_p = decision.get("user_prompt", "What input?")
                    
                    spinner = Spinner("typing...")
                    spinner.start()
                    try:
                        input_str = self.brain.query_ollama(
                            messages=self.history + [{"role": "user", "content": user_p}],
                            system_prompt=sys_p
                        ).strip()
                    finally:
                        spinner.stop()
                    
                    clean_input = input_str.strip('"\' \n')
                    print(f"[Action] Sending Input: '{clean_input}'")
                    self.cli.send_input(clean_input)
                    
                    self.history.append({"role": "user", "content": user_p})
                    self.history.append({"role": "assistant", "content": clean_input})
                
                else:
                    print("[Action] Waiting...")
                    time.sleep(2)

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n[!] User interrupted session.")
        except Exception as e:
            print(f"\n[!] Unexpected Error: {e}")
        finally:
            print("\nShutting down CLI...")
            self.cli.cleanup()

    def run_auto_improvement(self):
        print("\n--- Running Auto-Improvement Scanner ---")
        self.tasks.scan()
        suggestions_raw = self.tasks.list_tasks(status="suggestion")
        
        # Simple parsing of the CLI output to find IDs
        lines = suggestions_raw.splitlines()
        suggestion_ids = []
        for line in lines:
            if "💡" in line:
                parts = line.split()
                if parts:
                    suggestion_ids.append(parts[0]) # ID is first column

        if not suggestion_ids:
            print("No new suggestions found.")
            return

        print(f"\nFound {len(suggestion_ids)} suggestions.")
        target_id = suggestion_ids[0]
        print(f"Proposed Improvement ID: {target_id}")
        
        # Timeout Input Logic
        print("\nDo you want to implement this improvement now? (y/n)")
        print("Auto-accepting in 5 minutes (300s)...")
        
        user_response = [None]
        
        def input_thread():
            try:
                user_response[0] = input("Response > ").strip().lower()
            except:
                pass

        t = threading.Thread(target=input_thread, daemon=True)
        t.start()
        
        t.join(timeout=300) # 5 minutes
        
        should_run = False
        if user_response[0] is None:
            print("\n[Timeout] Auto-accepting...")
            should_run = True
        elif user_response[0].startswith('y'):
            should_run = True
        else:
            print("Skipping improvement.")
            return

        if should_run:
            print(f"Implementing Task {target_id}...")
            # Pick it
            self.tasks.pick_next() # Assumes simple stack or logic
            
            # Delegate to Subagent
            # We need to get the title to tell subagent what to do
            # Ideally improvements_manager would return structured data, but we are parsing CLI output
            # For now, let's just ask Subagent to "Resolve the currently valid task in improvements.json"
            
            print("Delegating implementation to Agent...")
            spinner = Spinner("Agent Coding...")
            spinner.start()
            try:
                res = self.subagent.execute_task(
                    "Read improvements.json, find the 'in_progress' item, and write code to implement the task described in its title. If it is a TODO, find the file and fix it."
                )
                print(f"\nResult: {res}")
                
                # Mark resolved
                self.tasks.resolve_current()
            finally:
                spinner.stop()


if __name__ == "__main__":
    # Default to the internal one
    script = os.path.join("core", "html_terminal.py")
        
    orchestrator = Orchestrator(script)
    
    try:
        # Task Selection Interface
        print("\n--- RLM Workspace Manager ---")
        
        goal = input("Enter your goal (or press Enter to skip to improvements): ").strip()
        
        if goal:
            orchestrator.run_goal(goal)
            
        # Post-Run Improvement Cycle
        orchestrator.run_auto_improvement()

    except KeyboardInterrupt:
        print("\nExiting.")
