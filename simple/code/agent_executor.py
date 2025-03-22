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
from typing import Any, List, Tuple, Union

from simple.agent_interactions import move_to_python, move_to_tool, return_to_normal, update_status_msg
from simple.code.inference import run_inference
from simple.code.system_prompts import MD_HEADING, load_message_template
from simple.code.utils import extract_json_block, colored_print, Fore
from simple.code.code_execute import execute_python_code, execute_tool
from simple.code.logging_config import setup_logging

setup_logging()


class AgentExecutor:
    def __init__(self, model_name: str, messages_context: List[dict] = None) -> None:
        self.model_name = model_name
        self.messages_context = messages_context if messages_context is not None else []
        self.summary: str = ""
        self.full_prompt: str = ""

    def _build_correction_prompt(self, base_prompt: List[dict], base_response: Any, hint: str) -> List[dict]:
        prompt = base_prompt.copy()
        prompt.append({'role': 'assistant', 'content': json.dumps(
            base_response) if not isinstance(base_response, str) else base_response})
        prompt.append({'role': 'user', 'content': hint})
        return prompt

    async def _get_valid_json_response(
        self,
        base_prompt: List[dict],
        scratchpad_widget: Any,
        root: Any,
        error_hint: str
    ) -> Tuple[dict, str, List[dict]]:
        """
        Helper that runs inference repeatedly until a valid JSON block is extracted.
        Returns the JSON object, the raw response, and the (potentially updated) prompt.
        """
        while True:
            base_response = run_inference(
                base_prompt, scratchpad_widget, root, self.model_name)
            try:
                json_resp = extract_json_block(base_response)
                # If the JSON is a list, take the first element.
                if isinstance(json_resp, list):
                    json_resp = json_resp[0]
                elif isinstance(json_resp, str):
                    raise ValueError(
                        "JSON block is a string instead of an object.")
                return json_resp, base_response, base_prompt
            except ValueError:
                base_prompt = self._build_correction_prompt(
                    base_prompt,
                    base_response,
                    error_hint
                )

    async def agent_execution(self, base_prompt: List[dict], output_widget: Any, scratchpad_widget: Any, root: Any) -> str:
        print("Agent AI")
        logging.debug("Base prompt for agent execution: %s", base_prompt)

        # Use the helper to ensure a valid JSON response.
        json_instruct, base_response, base_prompt = await self._get_valid_json_response(
            base_prompt, scratchpad_widget, root,
            "Wrap the instruction in triple backticks and specify 'json' (starting with ```json)."
        )

        if 'use' in json_instruct and json_instruct['use'].lower() in ['python', 'tool']:
            base_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            ai_choice = json_instruct["use"].lower()
            print(f"Starting {ai_choice.capitalize()} Use")
            responses = []
            if ai_choice == "python":
                move_to_python()
                py_base_prompt = load_message_template('python')
                py_base_prompt.append(
                    {'role': 'user', 'content': self.full_prompt})
                final_response, code_script, status_message, py_base_prompt = await self.code_use(py_base_prompt, scratchpad_widget, root)
                responses.append(
                    f"{MD_HEADING}{status_message}\n\n{MD_HEADING} Observations:\n{final_response}")
            elif ai_choice == "tool":
                move_to_tool()
                tool_base_prompt = load_message_template('tool')
                tool_base_prompt.append(
                    {'role': 'user', 'content': self.full_prompt})
                final_response, code_script, status_message, tool_base_prompt = await self.tool_use(tool_base_prompt, scratchpad_widget, root)
                responses.append(
                    f"{MD_HEADING}{status_message}\n\n{MD_HEADING} Observations:\n{final_response}")
                return_to_normal()

        else:
            # If the JSON does not contain the expected key, rebuild the prompt and try again.
            correction_prompt = self._build_correction_prompt(
                base_prompt, json.dumps(base_response),
                "Produce a JSON object with a 'use' key and value either python or tool."
            )
            return await self.agent_execution(correction_prompt, output_widget, scratchpad_widget, root)

        print("Checking Results")
        check_prompt = load_message_template('check', self.summary)
        check_prompt.append(
            {'role': 'user', 'content': f"Based on the following:\n{responses}\n\nWas the request '{self.full_prompt}' answered?"})
        check_response = run_inference(
            check_prompt, scratchpad_widget, root, self.model_name)
        # Ensure valid JSON from the check response
        json_check, _, base_prompt = await self._get_valid_json_response(
            check_prompt, scratchpad_widget, root,
            "Wrap the check response in triple backticks with a JSON object containing the key 'use' and a value of either yes or no."
        )
        if 'use' in json_check and json_check['use'].lower() in ['yes', 'no']:
            base_prompt.append(
                {'role': 'assistant', 'content': json.dumps(check_response)})
            ai_choice = json_check["use"].lower()
            if ai_choice == "yes":

                solve_base_prompt = load_message_template('answer')
                solve_base_prompt.append(
                    {'role': 'user', 'content': f"Based on the following:\n{responses}\n\nWhat is the final answer to the following request:\n'{self.full_prompt}'?"})
                final_response = run_inference(
                    solve_base_prompt, output_widget, root, self.model_name)
                return final_response
            else:
                print("Problem Not Solved")
                correction_prompt = self._build_correction_prompt(
                    base_prompt, json.dumps(check_response),
                    "Produce a JSON object with a 'use' key and value either python or tool."
                )
                return await self.agent_execution(correction_prompt, output_widget, scratchpad_widget, root)
        else:
            correction_prompt = self._build_correction_prompt(
                base_prompt, json.dumps(check_response),
                "Produce a JSON object with a 'use' key and value either python or tool."
            )
            return await self.agent_execution(correction_prompt, output_widget, scratchpad_widget, root)

    async def tool_use(self, base_prompt: List[dict], scratchpad_widget: Any, root: Any) -> Tuple[str, List[str], List[str], List[dict]]:
        # (Similar refactoring can be applied here using _get_valid_json_response)
        base_response = run_inference(
    base_prompt, scratchpad_widget, root, self.model_name)
        try:
            json_instruct = extract_json_block(base_response)
        except ValueError:
            correction_prompt = self._build_correction_prompt(
                base_prompt, base_response,
                "Wrap the instruction in triple backticks and specify 'json' (starting with ```json)."
            )
            return await self.tool_use(correction_prompt, scratchpad_widget, root)
        status_messages = []
        if isinstance(json_instruct, list):
            json_instruct = json_instruct[0]
        elif isinstance(json_instruct, str):
            correction_prompt = self._build_correction_prompt(
        base_prompt, base_response,
        "Wrap the instruction in triple backticks with a JSON object containing tool and parameters."
    )
            return await self.tool_use(correction_prompt, scratchpad_widget, root)
        status_message = execute_tool(json_instruct)
        update_status_msg(status_message)
        if status_message['status'] != "200":
            correction_prompt = self._build_correction_prompt(
            base_prompt, base_response,
        f"Generated tool instruction:\n{json.dumps(json_instruct)}\nExecution failed: {status_message['message']}\nFix the above error"
    )
            return await self.tool_use(correction_prompt, scratchpad_widget, root)
        else:
            base_prompt.append(
        {'role': 'assistant', 'content': json.dumps(base_response)})
            status_messages.append(status_message['message'])
            final_prompt = base_prompt.copy()
            final_prompt.append(
    {'role': 'user', 'content': f"Generated tool instruction:\n{json.dumps(json_instruct)}\nExecution result:\n{status_message['message']}"})
            final_response = run_inference(
    final_prompt, scratchpad_widget, root, self.model_name)
            base_prompt.append({'role': 'assistant', 'content': final_response})
            return final_response, json_instruct, status_messages, base_prompt

    async def code_use(self, base_prompt: List[dict], scratchpad_widget: Any, root: Any) -> Tuple[str, List[str], str, List[dict]]:
                # (A similar refactoring pattern can be applied to this method as well.)
        base_response = run_inference(
        base_prompt, scratchpad_widget, root, self.model_name)
        code_script = self.extract_code_blocks(base_response, 'python')
        status_message = execute_python_code("".join(code_script))
        update_status_msg(status_message)
        if status_message['status'] != "200":
            correction_prompt = self._build_correction_prompt(
              base_prompt, base_response,
               f"Tested code:\n{''.join(code_script)}\nExecution result:\n{status_message['message']}\nFix and complete the code"
            )
            return await self.code_use(correction_prompt, scratchpad_widget, root)
        else:
            base_prompt.append({'role': 'assistant', 'content': base_response})
            base_prompt.append(
              {'role': 'user', 'content': f"Generated code:\n{''.join(code_script)}\nExecution result:\n{status_message['message']}"})
            final_response = run_inference(
               base_prompt, scratchpad_widget, root, self.model_name)
            base_prompt.append(
                {'role': 'assistant', 'content': final_response})
            return final_response, code_script, status_message['message'], base_prompt

    async def decide_execution(self, text_prompt: dict, output_widget: Any, scratchpad_widget: Any, root: Any, full_prompt) -> str:
        self.full_prompt = full_prompt
        base_prompt = load_message_template('base', '')
        base_prompt.append(text_prompt)
        return await self.agent_execution(base_prompt, output_widget, scratchpad_widget, root)

    @staticmethod
    def extract_code_blocks(text: str, language: str) -> List[str]:
        try:
            pattern = rf"```(?:\n\s*)*{re.escape(language)}\s*\n(.*?)```"
            return re.findall(pattern, text, re.DOTALL)
        except Exception as e:
            print(e)
            return []
