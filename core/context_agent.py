import sys
import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

# Import shared utilities from parent (e.g. inference) if possible, 
# or we can pass the inference function in.
# For now, we'll duplicte/import the inference helper or assume it's passed.

class ContextAgent:
    """
    A subagent that uses rlm_repl.py to research the codebase and answer questions.
    """
    
    def __init__(self, inference_func, repl_script_path: Optional[str] = None):
        self.inference_func = inference_func
        
        if repl_script_path is None:
             # Default to sibling file 'rlm_repl.py' in the same directory
            repl_script_path = str(Path(__file__).parent / "rlm_repl.py")

        self.repl_script_path = Path(repl_script_path).resolve()
        self.max_steps = 5
        self.repl_state_path = Path(".flexi/rlm_state/state.pkl")
        
        # Ensure REPL is initialized
        self._init_repl()

    def _init_repl(self):
        """Initialize the REPL state if not exists."""
        if not self.repl_state_path.exists():
            # Initialize with current directory context or empty
            try:
                subprocess.run(
                    [sys.executable, str(self.repl_script_path), "init", "."],
                    check=True,
                    capture_output=True
                )
            except Exception as e:
                print(f"[SubAgent] Failed to init REPL: {e}")

    def _run_repl_code(self, code: str) -> str:
        """Execute code in the persistent REPL."""
        try:
            # We use the 'exec' command of rlm_repl.py
            # Using stdin to pass code
            process = subprocess.Popen(
                [sys.executable, str(self.repl_script_path), "exec"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd() # Run in current dir
            )
            stdout, stderr = process.communicate(input=code)
            
            output = stdout
            if stderr:
                output += f"\n[STDERR]\n{stderr}"
            return output.strip()
        except Exception as e:
            return f"Error executing REPL code: {e}"

    def execute_task(self, task: str) -> str:
        """
        Main entry point. Runs the agent loop to execute the task.
        """
        print(f"\n[SUBAGENT] Executing Task: {task}")
        
        history = []
        
        # Load prompt template
        try:
            with open("prompts/subagent_prompt.md", "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            return "Error: promts/subagent_prompt.md not found."
            
        for step in range(self.max_steps):
            # Format prompt
            prompt = prompt_template.format(
                query=task,
                cwd=os.getcwd(),
                history=json.dumps(history, indent=2)
            )
            
            messages = [{"role": "user", "content": prompt}]
            
            # Call LLM
            print(f"[SUBAGENT] Thinking (Step {step+1})...")
            response = self.inference_func(messages, model="gemma3:4b")
            
            # Parse JSON
            try:
                # Extract JSON block
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    response_json = json_match.group(1)
                else:
                    response_json = response
                
                plan = json.loads(response_json)
            except Exception as e:
                print(f"[SUBAGENT] Error parsing JSON: {e}")
                # Retry or note error
                history.append(f"Step {step+1} Error: Invalid JSON response from LLM.")
                continue
                
            # Check completion
            if plan.get("is_complete"):
                return plan.get("final_answer", "Task marked complete but no answer provided.")
            
            # Execute Code
            code = plan.get("python_code")
            if code:
                print(f"[SUBAGENT] Executing code:\n{code[:100]}...")
                output = self._run_repl_code(code)
                print(f"[SUBAGENT] Output:\n{output[:200]}...")
                
                history.append({
                    "step": step + 1,
                    "thought": plan.get("thought"),
                    "code": code,
                    "output": output
                })
            else:
                history.append({
                    "step": step + 1,
                    "thought": plan.get("thought"),
                    "error": "No code provided but not complete."
                })
                
        return "Subagent failed to find an answer within the step limit."
