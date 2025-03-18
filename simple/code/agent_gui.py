# Agentic System

# Process
# - Agentic System capable for running tools and executing code
# - the system should decide if it should get information from the vector database
# - the tool or code should get executed

# GUI
# - input text area for user to enter what they would like to do
# - text area scratchpad for run inference to show each step taken
# - the agent should work on the task in the scratchpad continuously until the retries run out or the task is complete
# - the final response should be written to the output area
import os
import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import threading
import asyncio
import json
import re
from typing import List
import logging

from simple.code import utils, memory
from simple.code.utils import colored_print, Fore, extract_json_block
from simple.code.inference import run_inference
from simple.code.history import HistoryManager
from simple.code.code_execute import execute_python_code, execute_tool
from simple.code.system_prompts import MD_HEADING, load_message_template
from simple.code.logging_config import setup_logging

# Centralized logging setup
setup_logging()

triple_backticks = '`' * 3


class FlexiAgentApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Flexi💻AI")
        self.set_app_icon()
        self.summary = ""
        self.messages_context = []  # initial system prompt context
        self.text_history = []
        self.model_var = tk.StringVar(value="llama3.2")

        # Main container with padding
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Model selection frame
        model_frame = tk.Frame(main_frame)
        model_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        self.model_entry = tk.Entry(model_frame, textvariable=self.model_var)
        self.model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Directory and tips frame for agent context
        directory_frame = tk.Frame(main_frame)
        directory_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(directory_frame, text="Agent Work Directory:").grid(
            row=0, column=0, sticky="w")
        self.codebase_path_entry = tk.Entry(directory_frame)
        self.codebase_path_entry.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Label(directory_frame, text="Additional Tips:").grid(
            row=1, column=0, sticky="w")
        self.tips_entry = tk.Text(directory_frame, height=3)
        self.tips_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Input text area
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(input_frame, text="Enter your request:").pack(anchor="w")
        self.input_text_area = tk.Text(input_frame, height=5)
        self.input_text_area.pack(fill=tk.BOTH, expand=True)

        # Submit button
        self.submit_button = tk.Button(
            main_frame, text="Submit", command=self.submit_text)
        self.submit_button.pack(pady=(0, 5))

        # Output area
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(output_frame, text="Output:").pack(anchor="w")
        self.output_text_area = ScrolledText(
            output_frame, height=10, bg="lightyellow")
        self.output_text_area.pack(fill=tk.BOTH, expand=True)

        # Scratchpad area for inference steps
        scratchpad_frame = tk.Frame(main_frame)
        scratchpad_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(scratchpad_frame, text="Scratchpad:").pack(anchor="w")
        self.agent_scratchpad_text_area = ScrolledText(
            scratchpad_frame, height=10, bg="lightgray")
        self.agent_scratchpad_text_area.pack(fill=tk.BOTH, expand=True)

        # User history area (read-only)
        history_frame = tk.Frame(main_frame)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(history_frame, text="User History:").pack(anchor="w")
        self.user_history = ScrolledText(
            history_frame, height=10, state=tk.DISABLED, bg="lightblue")
        self.user_history.pack(fill=tk.BOTH, expand=True)

    def set_app_icon(self) -> None:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.normpath(os.path.join(
                current_dir, "..", "gag", "artistic_plot.png"))
            if not os.path.exists(icon_path):
                from simple.makeArt import create_artistic_png
                default_data = [1, 3, 2, 5, 7, 8, 6]
                create_artistic_png(default_data, filename=icon_path)
                logging.info(
                    f"Icon file not found. Generated new icon at: {icon_path}")
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
        except Exception as e:
            logging.error(f"Failed to load custom icon: {e}")


    def run_async_in_thread(self, coroutine, callback):
        """Runs an async coroutine in a separate thread and calls the callback with the result."""
        def worker():
            try:
                result = asyncio.run(coroutine)
            except Exception as e:
                logging.exception("Error in asynchronous coroutine")
                result = f"Error: {str(e)}"
            self.root.after(0, callback, result)
        threading.Thread(target=worker).start()

    def submit_text(self) -> None:
        user_input = self.input_text_area.get("1.0", "end-1c")
        if not user_input.strip():
            return
        self.full_prompt = self.build_full_prompt(user_input)
        self.submit_button.config(state=tk.DISABLED)
        # Store prompt as a dict (convert to list later if needed)
        self.text_prompt = {'role': 'user', 'content': self.full_prompt}
        self.update_user_input_history()
        self.output_text_area.delete("1.0", tk.END)
        self.agent_scratchpad_text_area.delete("1.0", tk.END)
        # Run the asynchronous decision-making process
        self.run_async_in_thread(self.decide_execution(
            self.text_prompt), self.handle_response)

    def handle_response(self, response: str) -> None:
        """Updates the UI with the final response and re-enables the submit button."""
        if isinstance(self.text_prompt, dict):
            self.text_prompt = [self.text_prompt]
        self.text_prompt.append({'role': 'assistant', 'content': response})
        self.output_text_area.insert(tk.END, "\n" + response)
        self.submit_button.config(state=tk.NORMAL)

    @staticmethod
    def extract_code_blocks(text: str, language: str) -> list:
        # Regex to extract code blocks (triple backticks followed by language)
        pattern = rf"```(?:\n\s*)*{re.escape(language)}\s*\n(.*?)```"
        return re.findall(pattern, text, re.DOTALL)

    async def decide_execution(self, messages: dict) -> str:
        base_prompt = load_message_template('base', '')
        base_prompt.append(messages)
        return await self.agent_execution(base_prompt)

    async def tool_use(self, base_prompt: List[dict]):
        base_response = run_inference(
            base_prompt, self.agent_scratchpad_text_area, self.root, self.model_var.get())
        tool_script = self.extract_code_blocks(base_response, 'json')
        if not tool_script:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            correction_prompt.append(
                {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json'."})
            return await self.tool_use(correction_prompt)
        status_messages = []
        for code_snippet in tool_script:
            try:
                json_instruct = json.loads(code_snippet)
            except json.JSONDecodeError:
                continue
            if isinstance(json_instruct, list):
                json_instruct = json_instruct[0]
            elif isinstance(json_instruct, str):
                correction_prompt = base_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                correction_prompt.append(
                    {'role': 'user', 'content': "Wrap the instruction in triple backticks with a JSON object containing tool and parameters."})
                return await self.tool_use(correction_prompt)
            status_message = execute_tool(json_instruct)
            if status_message['status'] != "200":
                new_prompt = base_prompt.copy()
                new_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                new_prompt.append(
                    {'role': 'user', 'content': f"{MD_HEADING} Generated tool instruction:\n\n{json.dumps(tool_script)}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}\n\n{MD_HEADING} Fix the above error"})
                return await self.tool_use(new_prompt)
            else:
                base_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                status_messages.append(status_message)
            final_prompt = base_prompt.copy()
            final_prompt.append(
                {'role': 'user', 'content': f"{MD_HEADING} Generated tool instruction:\n\n{code_snippet}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}"})
            final_response = run_inference(
                final_prompt, self.agent_scratchpad_text_area, self.root, self.model_var.get())
            base_prompt.append(
                {'role': 'assistant', 'content': final_response})
            return final_response, tool_script, status_messages, base_prompt

    async def code_use(self, base_prompt: List[dict]):
        base_response = run_inference(
            base_prompt, self.agent_scratchpad_text_area, self.root, self.model_var.get())
        code_script = self.extract_code_blocks(base_response, 'python')
        status_message = execute_python_code("".join(code_script))
        if status_message['status'] != "200":
            new_prompt = base_prompt.copy()
            new_prompt.append({'role': 'assistant', 'content': base_response})
            new_prompt.append(
                {'role': 'user', 'content': f"{MD_HEADING} Generated code:\n\n{''.join(code_script)}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}"})
            return await self.code_use(new_prompt)
        else:
            base_prompt.append({'role': 'assistant', 'content': base_response})
            base_prompt.append(
                {'role': 'user', 'content': f"{MD_HEADING} Generated code:\n\n{''.join(code_script)}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}"})
            final_response = run_inference(
                base_prompt, self.agent_scratchpad_text_area, self.root, self.model_var.get())
            base_prompt.append(
                {'role': 'assistant', 'content': final_response})
            return final_response, code_script, status_message, base_prompt

    async def agent_execution(self, base_prompt: List[dict]):
        colored_print("Agent AI", Fore.BLUE)
        logging.debug("Base prompt for agent execution: %s", base_prompt)
        base_response = run_inference(
            base_prompt, self.agent_scratchpad_text_area, self.root, self.model_var.get())

        try:
            json_instruct = extract_json_block(base_response)
        except ValueError:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': base_response})
            correction_prompt.append(
                {'role': 'user', 'content': "Wrap the instruction in triple backticks and specify 'json' (starting with ```json)."})
            return await self.agent_execution(correction_prompt)

        responses = []
        if isinstance(json_instruct, list):
            json_instruct = json_instruct[0]
        elif isinstance(json_instruct, str):
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            correction_prompt.append(
                {'role': 'user', 'content': "Wrap the instruction in triple backticks with a JSON object containing the key 'use' and a value of either python or tool."})
            return await self.agent_execution(correction_prompt)

        if 'use' in json_instruct and json_instruct['use'].lower() in ['python', 'tool']:
            base_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            ai_choice = json_instruct["use"].lower()

            if ai_choice == "python":
                colored_print("Starting Python Code Use", Fore.BLUE)
                py_base_prompt = self.messages_context + \
                    load_message_template('python')
                py_base_prompt.append(self.text_prompt)
                final_response, code_script, status_message, py_base_prompt = await self.code_use(py_base_prompt)
                responses.append({
                    'response': final_response,
                    'code': code_script,
                    'status': status_message,
                    'request': py_base_prompt
                })
            elif ai_choice == "tool":
                colored_print("Starting Tool Use", Fore.BLUE)
                tool_base_prompt = self.messages_context + \
                    load_message_template('tool')
                tool_base_prompt.append(self.text_prompt)
                base_response, code_script, status_message, tool_base_prompt = await self.tool_use(tool_base_prompt)
                responses.append({
                    'response': base_response,
                    'instruction': code_script,
                    'status': status_message,
                    'request': tool_base_prompt
                })
        else:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            correction_prompt.append(
                {'role': 'user', 'content': "Produce a JSON object with a 'use' key and value either python or tool."})
            return await self.agent_execution(correction_prompt)

        if responses:
            colored_print("Checking Results", Fore.BLUE)
            check_prompt = self.messages_context + \
                load_message_template('check', self.summary)
            check_prompt.append(
                {'role': 'user', 'content': f"Based on the following:\n{responses}\n\nWas the request '{self.full_prompt}' answered?"})
            check_response = run_inference(
                check_prompt, self.agent_scratchpad_text_area, self.root, self.model_var.get())

            try:
                json_instruct = extract_json_block(check_response)
            except ValueError:
                correction_prompt = base_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': check_response})
                correction_prompt.append(
                    {'role': 'user', 'content': "Wrap the check response in triple backticks and specify 'json' (starting with ```json)."})
                return await self.agent_execution(correction_prompt)

            if isinstance(json_instruct, list):
                json_instruct = json_instruct[0]
            elif isinstance(json_instruct, str):
                correction_prompt = base_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(check_response)})
                correction_prompt.append(
                    {'role': 'user', 'content': "Wrap the check response in triple backticks with a JSON object containing the key 'use' and a value either python or tool."})
                return await self.agent_execution(correction_prompt)

            if 'use' in json_instruct and json_instruct['use'].lower() in ['yes', 'no']:
                base_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(check_response)})
                ai_choice = json_instruct["use"].lower()
                colored_print(ai_choice, Fore.CYAN)
                if ai_choice == "yes":
                    colored_print("Problem Solved", Fore.GREEN)
                    solve_base_prompt = self.messages_context + \
                        load_message_template('answer')
                    solve_base_prompt.append(
                        {'role': 'user', 'content': f"Based on the following:\n{responses}\n\nWhat is the final answer to '{self.full_prompt}'?"})
                    final_response = run_inference(
                        solve_base_prompt, self.output_text_area, self.root, self.model_var.get())
                    return final_response
                else:
                    colored_print("Problem Not Solved", Fore.RED)
                    correction_prompt = base_prompt.copy()
                    correction_prompt.append(
                        {'role': 'assistant', 'content': json.dumps(check_response)})
                    correction_prompt.append(
                        {'role': 'user', 'content': "Produce a JSON object with a 'use' key and value either python or tool."})
                    return await self.agent_execution(correction_prompt)
            else:
                correction_prompt = base_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(check_response)})
                correction_prompt.append(
                    {'role': 'user', 'content': "Produce a JSON object with a 'use' key and value either python or tool."})
                return await self.agent_execution(correction_prompt)

    def build_full_prompt(self, user_input: str) -> str:
        codebase_path = self.codebase_path_entry.get().strip()
        base_code = ""
        if codebase_path:
            try:
                base_code_list = utils.code_corpus(codebase_path)
                base_code = "\n".join(base_code_list)
            except Exception as e:
                logging.error(f"Error reading codebase: {e}")

        tips = self.tips_entry.get("1.0", "end-1c").strip()

        # Combine codebase, user input, and additional tips if provided.
        if base_code and tips:
            full_prompt = f"{MD_HEADING} Codebase:\n{base_code}\n\n{MD_HEADING} Request:\n{user_input}\n\nTips:\n{tips}"
        elif base_code:
            full_prompt = f"{MD_HEADING} Codebase:\n{base_code}\n\n{MD_HEADING} Request:\n{user_input}"
        elif tips:
            full_prompt = f"{MD_HEADING} Request:\n{user_input}\n\nTips:\n{tips}"
        else:
            full_prompt = f"{MD_HEADING} Request:\n{user_input}"
        return full_prompt

    def update_user_input_history(self) -> None:
        self.text_history.append(self.input_text_area.get("1.0", "end-1c"))
        self.user_history.config(state=tk.NORMAL)
        self.user_history.delete("1.0", tk.END)
        self.user_history.insert(tk.END, "\n".join(self.text_history))
        self.user_history.config(state=tk.DISABLED)


def main() -> None:
    root = tk.Tk()
    app = FlexiAgentApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
