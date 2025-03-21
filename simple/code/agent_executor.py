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
#!/usr/bin/env python3
"""
Agent Execution Module

This module contains the asynchronous logic for deciding how to handle user requests.
It uses helper functions (e.g. code execution and tool usage) while staying independent
of any GUI elements.
"""

import json
import logging
import re
from simple.code.inference import run_inference
from simple.code.system_prompts import MD_HEADING, load_message_template
from simple.code.utils import extract_json_block, colored_print, Fore
from simple.code.code_execute import execute_python_code, execute_tool
from simple.code.logging_config import setup_logging

setup_logging()


class AgentExecutor:
    def __init__(self, model_name: str, messages_context=None):
        self.model_name = model_name
        self.messages_context = messages_context if messages_context is not None else []
        self.summary = ""
        self.full_prompt = ""

    async def decide_execution(self, text_prompt: dict) -> str:
        base_prompt = load_message_template('base', '')
        base_prompt.append(text_prompt)
        return await self.agent_execution(base_prompt)

    async def tool_use(self, base_prompt: list, scratchpad_widget, root):
        base_response = run_inference(
            base_prompt, scratchpad_widget, root, self.model_name)
        tool_script = self.extract_code_blocks(base_response, 'json')
        if not tool_script:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            correction_prompt.append(
                {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json'."})
            return await self.tool_use(correction_prompt, scratchpad_widget, root)
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
                return await self.tool_use(correction_prompt, scratchpad_widget, root)
            status_message = execute_tool(json_instruct)
            if status_message['status'] != "200":
                new_prompt = base_prompt.copy()
                new_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                new_prompt.append(
                    {'role': 'user', 'content': f"{MD_HEADING} Generated tool instruction:\n\n{json.dumps(tool_script)}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}\n\n{MD_HEADING} Fix the above error"})
                return await self.tool_use(new_prompt, scratchpad_widget, root)
            else:
                base_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                status_messages.append(status_message['message'])
            final_prompt = base_prompt.copy()
            final_prompt.append(
                {'role': 'user', 'content': f"{MD_HEADING} Generated tool instruction:\n\n{code_snippet}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}"})
            final_response = run_inference(
                final_prompt, scratchpad_widget, root, self.model_name)
            base_prompt.append(
                {'role': 'assistant', 'content': final_response})
        return final_response, tool_script, status_messages, base_prompt

    async def code_use(self, base_prompt: list, scratchpad_widget, root):
        base_response = run_inference(
            base_prompt, scratchpad_widget, root, self.model_name)
        code_script = self.extract_code_blocks(base_response, 'python')
        status_message = execute_python_code("".join(code_script))
        if status_message['status'] != "200":
            new_prompt = base_prompt.copy()
            new_prompt.append({'role': 'assistant', 'content': base_response})
            new_prompt.append(
                {'role': 'user', 'content': f"{MD_HEADING} Tested code:\n\n{''.join(code_script)}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}\n\n{MD_HEADING} Fix and complete the code"})
            return await self.code_use(new_prompt, scratchpad_widget, root)
        else:
            base_prompt.append({'role': 'assistant', 'content': base_response})
            base_prompt.append(
                {'role': 'user', 'content': f"{MD_HEADING} Generated code:\n\n{''.join(code_script)}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}"})
            final_response = run_inference(
                base_prompt, scratchpad_widget, root, self.model_name)
            base_prompt.append(
                {'role': 'assistant', 'content': final_response})
            return final_response, code_script, status_message['message'], base_prompt

    async def agent_execution(self, base_prompt: list) -> str:
        colored_print("Agent AI", Fore.BLUE)
        logging.debug("Base prompt for agent execution: %s", base_prompt)
        base_response = run_inference(base_prompt, None, None, self.model_name)
        try:
            json_instruct = extract_json_block(base_response)
        except ValueError:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': base_response})
            correction_prompt.append(
                {'role': 'user', 'content': "Wrap the instruction in triple backticks and specify 'json' (starting with ```json)."})
            return await self.agent_execution(correction_prompt)
        if isinstance(json_instruct, list):
            json_instruct = json_instruct[0]
        elif isinstance(json_instruct, str):
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            correction_prompt.append(
                {'role': 'user', 'content': "Wrap the instruction in triple backticks with a JSON object containing the key 'use' and a value of either python or tool."})
            return await self.agent_execution(correction_prompt)
        responses = []
        if 'use' in json_instruct and json_instruct['use'].lower() in ['python', 'tool']:
            base_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            ai_choice = json_instruct["use"].lower()
            colored_print(f"Starting {ai_choice.capitalize()} Use", Fore.BLUE)
            if ai_choice == "python":
                py_base_prompt = load_message_template('python')
                py_base_prompt.append(
                    {'role': 'user', 'content': self.full_prompt})
                final_response, code_script, status_message, py_base_prompt = await self.code_use(py_base_prompt, None, None)
                responses.append(final_response)
            elif ai_choice == "tool":
                tool_base_prompt = load_message_template('tool')
                tool_base_prompt.append(
                    {'role': 'user', 'content': self.full_prompt})
                final_response, code_script, status_message, tool_base_prompt = await self.tool_use(tool_base_prompt, None, None)
                responses.append(final_response)
        else:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            correction_prompt.append(
                {'role': 'user', 'content': "Produce a JSON object with a 'use' key and value either python or tool."})
            return await self.agent_execution(correction_prompt)

        colored_print("Checking Results", Fore.BLUE)
        check_prompt = load_message_template('check', self.summary)
        check_prompt.append(
            {'role': 'user', 'content': f"Based on the following:\n{responses}\n\n{status_message}\n\nWas the request '{self.full_prompt}' answered?"})
        check_response = run_inference(
            check_prompt, None, None, self.model_name)
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
                solve_base_prompt = load_message_template('answer')
                solve_base_prompt.append(
                    {'role': 'user', 'content': f"Based on the following:\n{responses}\n\nWhat is the final answer to the following request:\n'{self.full_prompt}'?"})
                final_response = run_inference(
                    solve_base_prompt, None, None, self.model_name)
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

    @staticmethod
    def extract_code_blocks(text: str, language: str) -> list:
        pattern = rf"```(?:\n\s*)*{re.escape(language)}\s*\n(.*?)```"
        return re.findall(pattern, text, re.DOTALL)
