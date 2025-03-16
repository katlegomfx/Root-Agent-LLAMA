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


import sys
import tkinter as tk
from tkinter import filedialog
import threading
import asyncio
import json
import re
import io
import contextlib
from datetime import datetime
from typing import List

from simple.code import utils, memory
from simple.code.inference import run_inference, current_client
from simple.code.history import HistoryManager
from simple.code.function_call import execute_python_code, execute_tool
from simple.code.system_prompts import MD_HEADING, tool_registry, load_message_template
from colorama import Fore, Style

triple_backticks = '`'*3
USE_COLOR = sys.stdout.isatty()


def colored_print(text: str, color: str = Fore.RESET, end: str = "\n", flush: bool = False):
    """
    Prints the given text in the specified color, resetting style afterward.
    Only prints color codes if USE_COLOR is True.
    """
    if USE_COLOR:
        print(f"{color}{text}{Style.RESET_ALL}", end=end, flush=flush)
    else:
        print(text, end=end, flush=flush)


class FlexiAgentApp:
    def __init__(self, root: tk.Tk) -> None:
        pass

    def submit_text(self) -> None:
        user_input = self.input_text_area.get("1.0", "end-1c")
        if not user_input.strip():
            return
        full_prompt = self.build_full_prompt(user_input)
        self.submit_button.config(state=tk.DISABLED)
        self.text_prompt.append({'role': 'user', 'content': full_prompt})
        self.update_user_input_history()
        # Clear both output and scratchpad areas
        self.output_text_area.delete("1.0", tk.END)
        self.scratchpad_text_area.delete("1.0", tk.END)

        response = asyncio.run(
            self.decide_execution(self.text_prompt))
        self.text_prompt.append(
            {'role': 'assistant', 'content': response})

    @staticmethod
    def extract_code_blocks(text: str, language: str) -> list:
        pattern = rf"```{re.escape(language)}\s*\n(.*?)```"
        return re.findall(pattern, text, re.DOTALL)

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
                    {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json' with an object containing tool and parameters."})
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
                final_prompt, self.output_text_area, self.root, self.model_var.get())
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
                base_prompt, self.output_text_area, self.root, self.model_var.get())
            base_prompt.append(
                {'role': 'assistant', 'content': final_response})
            return final_response, code_script, status_message, base_prompt

    async def agent_execution(self, prompt: str):
        colored_print("Deciding using AI", Fore.GREEN)
        base_prompt = self.messages_context + \
            load_message_template('base', self.summary)
        base_prompt.append({'role': 'user', 'content': prompt})
        base_response = run_inference(
            base_prompt, self.agent_scratchpad_text_area, self.root, self.model_var.get())
        
        use_script = self.extract_code_blocks(base_response, 'json')
        if not use_script:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': base_response})
            correction_prompt.append(
                {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json'. (start response with ```json)"})
            return await self.agent_execution(correction_prompt)
        
        responses = []
        for code_snippet in use_script:
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
                    {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json' with an object containing the key 'use' and a 'value' either python or tool."})
                return await self.agent_execution(correction_prompt)

            if 'use' in json_instruct and json_instruct['use'].lower() in ['python', 'tool']:
                base_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})

                ai_choice = json_instruct["use"].lower()

                if ai_choice == "python":
                    colored_print("Starting Python Code Use", Fore.GREEN)
                    py_base_prompt = self.messages_context + \
                        load_message_template('python')
                    py_base_prompt.append({'role': 'user', 'content': prompt})
                    final_response, code_script, status_message, py_base_prompt = await self.code_use(py_base_prompt)
                    responses.append(
                        {
                            'response': final_response,
                            'code': code_script,
                            'status': status_message,
                            'request': py_base_prompt
                        }
                    )

                elif ai_choice == "tool":
                    colored_print("Starting Tool Use", Fore.GREEN)
                    tool_base_prompt = self.messages_context + \
                        load_message_template('tool')
                    tool_base_prompt.append(
                        {'role': 'user', 'content': prompt})
                    base_response, code_script, status_message, tool_base_prompt = await self.tool_use(tool_base_prompt)
                    responses.append(
                        {
                            'response': base_response,
                            'instruction': code_script,
                            'status': status_message,
                            'request': tool_base_prompt
                        }
                    )
            else:
                correction_prompt = base_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                correction_prompt.append(
                    {'role': 'user', 'content': "Please produce a JSON object with 'use' key and python or tool as 'value'."})
                return await self.agent_execution(correction_prompt)
        
        if len(responses) >= 1:
            check_prompt = self.messages_context + \
                load_message_template('check', self.summary)
            check_prompt.append({'role': 'user', 'content': f"Based on the following:\n{responses}\n\nWas the request {prompt} answered?"})
            check_response = run_inference(
                check_prompt, self.agent_scratchpad_text_area, self.root, self.model_var.get())

            use_script = self.extract_code_blocks(check_response, 'json')
            if not use_script:
                correction_prompt = check_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': check_response})
                correction_prompt.append(
                    {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json'. (start response with ```json)"})
                return await self.agent_execution(correction_prompt)
            for code_snippet in use_script:
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
                        {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json' with an object containing the key 'use' and a 'value' either python or tool."})
                    return await self.agent_execution(correction_prompt)

            if 'use' in json_instruct and json_instruct['use'].lower() in ['yes', 'no']:
                base_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})

                ai_choice = json_instruct["use"].lower()

                if ai_choice == "yes":
                    colored_print("Was Solved", Fore.GREEN)
                    solve_base_prompt = self.messages_context + \
                        load_message_template('answer')
                    solve_base_prompt.append({'role': 'user', 'content': f"Based on the following:\n{responses}\n\nWhat is the final answer to '{prompt}'?"})
                    final_response = await self.code_use(solve_base_prompt)
                    return final_response

                elif ai_choice == "no":
                    colored_print("Was not Solved", Fore.RED)
                    correction_prompt.append(
                        {'role': 'assistant', 'content': json.dumps(base_response)})
                    correction_prompt.append(
                        {'role': 'user', 'content': "Please produce a JSON object with 'use' key and python or tool as 'value'."})
                    return await self.agent_execution(correction_prompt)
                    
            else:
                correction_prompt = base_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                correction_prompt.append(
                    {'role': 'user', 'content': "Please produce a JSON object with 'use' key and python or tool as 'value'."})
                return await self.agent_execution(correction_prompt)



def main() -> None:
    root = tk.Tk()
    app = FlexiAgentApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
