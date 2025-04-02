import json
import logging
import re
from typing import Any, List, Optional, Tuple, Dict, Union  # Added Dict, Union

from simple.agent_interactions import AgentInteractionManager
from simple.code.inference import run_inference
from simple.code.system_prompts import MD_HEADING, load_message_template
from simple.code.utils import extract_json_block, colored_print, Fore
from simple.code.code_execute import execute_python_code, execute_tool


MAX_RETRIES = 3  # Reduced default retries to 3 for faster failure if stuck
JSON_ERROR_HINT = "Invalid JSON. Provide a valid JSON object wrapped in triple backticks (```json ... ```)."
USE_KEY_ERROR_HINT = "JSON requires a 'use' key with value 'python', 'tool', or 'respond'."
CHECK_KEY_ERROR_HINT = "JSON requires a 'use' key with value 'yes' or 'no'."


class AgentExecutor:
    def __init__(self, model_name: str, messages_context: List[dict] = None,
                 agent_manager: AgentInteractionManager = None) -> None:
        self.model_name = model_name
        self.messages_context = messages_context if messages_context is not None else []
        self.summary: str = ""
        self.full_prompt: str = ""
        self.agent_manager = agent_manager if agent_manager is not None else AgentInteractionManager()
        self.current_retries = 0  # Track retries per execution cycle

    def _build_correction_prompt(self, base_prompt: List[dict], bad_response: Any, hint: str) -> List[dict]:
        """Appends the bad response and a correction hint to the prompt history."""
        prompt = base_prompt.copy()
        assistant_content = json.dumps(bad_response) if not isinstance(
            bad_response, str) else bad_response
        prompt.append({'role': 'assistant', 'content': assistant_content})
        prompt.append({'role': 'user', 'content': hint})
        logging.warning(f"Correction needed. Hint: {hint}")
        return prompt

    async def _get_valid_json_response(self, base_prompt: List[dict], scratchpad_widget: Any,
                                       root: Any, error_hint: str, max_retries: int = MAX_RETRIES) -> Tuple[Optional[Union[Dict, List]], str, List[dict]]:
        """Attempts to get a valid JSON response from the model, with retries."""
        retries = 0
        current_prompt = base_prompt
        while retries < max_retries:
            raw_response = run_inference(
                current_prompt, scratchpad_widget, root, self.model_name)
            try:
                json_resp = extract_json_block(raw_response)
                return json_resp, raw_response, current_prompt
            except ValueError as e:
                logging.warning(
                    f"JSON extraction/validation failed (Attempt {retries + 1}/{max_retries}): {e}")
                retries += 1
                current_prompt = self._build_correction_prompt(
                    current_prompt, raw_response, f"{error_hint} Error: {e}"
                )
            except Exception as e:  # Catch other potential errors during inference/parsing
                logging.error(
                    f"Unexpected error getting JSON response (Attempt {retries + 1}/{max_retries}): {e}")
                retries += 1
                current_prompt = self._build_correction_prompt(
                    current_prompt, raw_response, f"Unexpected error occurred: {e}. {error_hint}"
                )

        logging.error(
            f"Failed to get valid JSON response after {max_retries} retries.")
        return None, raw_response, current_prompt

    async def agent_execution(self, base_prompt: List[dict], output_widget: Any,
                              scratchpad_widget: Any, root: Any) -> Tuple[str, str]:
        """Main agent execution loop: Decide -> Act (Python/Tool/Respond) -> Check -> Final Answer."""
        logging.info("=== Starting Agent Execution Cycle ===")
        action_log = ""
        self.current_retries = 0  # Reset retries for this cycle

        while self.current_retries < MAX_RETRIES:
            logging.info(
                f"--- Agent Step (Attempt {self.current_retries + 1}/{MAX_RETRIES}) ---")
            colored_print("Step 1: Deciding Action...", Fore.CYAN)
            json_instruct, raw_response, current_prompt = await self._get_valid_json_response(
                base_prompt, scratchpad_widget, root, JSON_ERROR_HINT
            )

            if json_instruct is None:
                final_response = "Agent failed to decide on an action after multiple retries."
                action_log += f"\n[Decision Error]\n{final_response}\nRaw Response:\n{raw_response}"
                self.current_retries = MAX_RETRIES  # Break loop
                continue  # Go to end of loop

            if not isinstance(json_instruct, dict) or 'use' not in json_instruct:
                current_prompt = self._build_correction_prompt(
                    current_prompt, raw_response, USE_KEY_ERROR_HINT)
                self.current_retries += 1
                continue  # Retry decision

            ai_choice = str(json_instruct.get("use", "")).lower()
            if ai_choice not in ['python', 'tool', 'respond']:
                current_prompt = self._build_correction_prompt(
                    current_prompt, raw_response, USE_KEY_ERROR_HINT + f" Got: '{ai_choice}'")
                self.current_retries += 1
                continue  # Retry decision

            current_prompt.append(
                {'role': 'assistant', 'content': raw_response})
            base_prompt = current_prompt  # Update base for next potential loop iteration

            colored_print(f"Decision: Use '{ai_choice}'", Fore.BLUE)
            action_log += f"\n[Decision]\nChoice: {ai_choice}\nRationale (implied): {raw_response}\n"

            final_response = ""
            execution_successful = False

            if ai_choice == "python":
                colored_print("Step 2: Executing Python Code...", Fore.CYAN)
                self.agent_manager.move_to_python()
                py_base_prompt = load_message_template(
                    'python', self.summary)  # Pass summary
                py_base_prompt.append(
                    {'role': 'user', 'content': f"Based on the request:\n'{self.full_prompt}'\nGenerate the necessary Python code."})

                exec_response, code_script, status_message, py_base_prompt_result = await self.code_use(
                    py_base_prompt, scratchpad_widget, root)

                action_log += (
                    f"\n[Python Code Execution]\n"
                    f"Code:\n```python\n{''.join(code_script)}\n```\n"
                    f"Status: {status_message}\n"
                    f"Result/Response: {exec_response}\n"
                )
                if status_message != "Max retries reached.":  # Check for success based on message content
                    execution_successful = True
                    final_response = exec_response  # Use the response generated after code execution

            elif ai_choice == "tool":
                colored_print("Step 2: Executing Tool...", Fore.CYAN)
                self.agent_manager.move_to_tool()
                tool_base_prompt = load_message_template(
                    'tool', self.summary)  # Pass summary
                tool_base_prompt.append(
                    {'role': 'user', 'content': f"Based on the request:\n'{self.full_prompt}'\nSelect and configure the appropriate tool."})

                exec_response, tool_instruct, status_messages, tool_base_prompt_result = await self.tool_use(
                    tool_base_prompt, scratchpad_widget, root)

                status_msg_str = "\n".join(status_messages)
                action_log += (
                    f"\n[Tool Execution]\n"
                    f"Instruction:\n```json\n{json.dumps(tool_instruct, indent=2)}\n```\n"
                    f"Status: {status_msg_str}\n"
                    f"Result/Response: {exec_response}\n"
                )
                if "Max retries reached." not in status_msg_str:  # Check for success
                    execution_successful = True
                    final_response = exec_response  # Use the response generated after tool execution

            elif ai_choice == "respond":
                colored_print(
                    "Step 2: Generating Direct Response...", Fore.CYAN)
                solve_base_prompt = load_message_template(
                    'answer', self.summary)
                solve_base_prompt.append(
                    {'role': 'user', 'content': f"Provide a direct final answer to the following request:\n'{self.full_prompt}'?"}
                )
                final_response = run_inference(
                    solve_base_prompt, output_widget, root, self.model_name)
                action_log += f"\n[Direct Response]\nAnswer: {final_response}\n"
                self.agent_manager.return_to_normal()  # Ensure agent returns visually
                return final_response, action_log

            self.agent_manager.return_to_normal()

            if not execution_successful:
                colored_print(
                    "Execution failed, retrying decision...", Fore.YELLOW)
                self.current_retries += 1
                base_prompt.append(
                    {'role': 'user', 'content': f"The previous attempt to use '{ai_choice}' failed. Review the log:\n{action_log}\nReassess the best approach ('python', 'tool', or 'respond') to fulfill the request: '{self.full_prompt}'"})
                continue  # Go to the start of the while loop

            colored_print(
                "Step 3: Checking if Request Fulfilled...", Fore.CYAN)
            check_prompt = load_message_template('check', self.summary)
            check_prompt.append({
                'role': 'user',
                'content': f"Review the execution log:\n{action_log}\n\nBased *only* on this log, was the original request '{self.full_prompt}' successfully fulfilled? Respond yes or no."
            })

            json_check, raw_check_response, check_prompt = await self._get_valid_json_response(
                check_prompt, scratchpad_widget, root, CHECK_KEY_ERROR_HINT
            )

            if json_check is None:
                final_response = "Agent failed to check the result after multiple retries."
                action_log += f"\n[Check Error]\n{final_response}\nRaw Response:\n{raw_check_response}"
                self.current_retries = MAX_RETRIES  # Break loop
                continue  # Go to end of loop

            if not isinstance(json_check, dict) or 'use' not in json_check:
                base_prompt = self._build_correction_prompt(
                    check_prompt, raw_check_response, CHECK_KEY_ERROR_HINT)
                self.current_retries += 1
                continue

            check_choice = str(json_check.get("use", "")).lower()
            if check_choice not in ['yes', 'no']:
                base_prompt = self._build_correction_prompt(
                    check_prompt, raw_check_response, CHECK_KEY_ERROR_HINT + f" Got: '{check_choice}'")
                self.current_retries += 1
                continue  # Retry

            current_prompt = check_prompt  # Start from the check prompt context
            current_prompt.append(
                {'role': 'assistant', 'content': raw_check_response})
            base_prompt = current_prompt  # Update base prompt

            action_log += f"\n[Check Result]\nFulfilled: {check_choice}\n"
            colored_print(f"Request fulfilled: {check_choice}", Fore.BLUE)

            if check_choice == "yes":
                colored_print("Step 4: Generating Final Answer...", Fore.CYAN)
                solve_base_prompt = load_message_template(
                    'answer', self.summary)
                solve_base_prompt.append({
                    'role': 'user',
                    'content': f"Based on the following execution log:\n{action_log}\n\nProvide the final, comprehensive answer to the original request:\n'{self.full_prompt}'"
                })
                final_answer = run_inference(
                    solve_base_prompt, output_widget, root, self.model_name)
                action_log += f"\n[Final Answer]\n{final_answer}\n"
                logging.info(
                    "=== Agent Execution Cycle Completed Successfully ===")
                return final_answer, action_log
            else:
                colored_print(
                    "Request not fulfilled, continuing execution...", Fore.YELLOW)
                self.current_retries += 1
                base_prompt.append(
                    {'role': 'user', 'content': f"The request '{self.full_prompt}' was not fulfilled. Review the log:\n{action_log}\nDecide the *next* step ('python', 'tool', or 'respond')."})

        logging.error(f"Agent execution failed after {MAX_RETRIES} attempts.")
        final_response = final_response or "Agent execution failed to complete after maximum retries."
        action_log += "\n[Execution Failed]\nAgent stopped after maximum retries.\n"
        return final_response, action_log

    async def tool_use(self, base_prompt: List[dict], scratchpad_widget: Any, root: Any) -> Tuple[str, Dict, List[str], List[dict]]:
        """Handles the process of selecting, executing, and responding to a tool use."""
        retries = 0
        current_prompt = base_prompt
        tool_instruct: Dict = {}
        status_messages: List[str] = ["Tool use not attempted."]

        while retries < MAX_RETRIES:
            logging.info(
                f"--- Tool Use Step (Attempt {retries + 1}/{MAX_RETRIES}) ---")
            json_resp, raw_response, current_prompt = await self._get_valid_json_response(
                current_prompt, scratchpad_widget, root,
                "Provide a JSON object with 'tool' and 'parameters' keys, wrapped in ```json.",
                max_retries=1  # Only one try to get the instruction per outer loop attempt
            )

            if json_resp is None or not isinstance(json_resp, dict) or 'tool' not in json_resp:
                logging.warning("Failed to get valid tool instruction JSON.")
                status_messages = [
                    "Failed to generate valid tool instruction."]
                current_prompt = self._build_correction_prompt(
                    current_prompt, raw_response,
                    "Invalid tool instruction. Provide a JSON object with 'tool' and 'parameters' keys."
                )
                retries += 1  # Consume a retry for the tool_use cycle
                continue  # Try getting instruction again in next loop

            tool_instruct = json_resp  # Got valid instruction structure
            current_prompt.append(
                {'role': 'assistant', 'content': raw_response})

            colored_print(
                f"Executing Tool: {tool_instruct.get('tool')}...", Fore.GREEN)
            status_result = execute_tool(
                tool_instruct, self.agent_manager)  # Pass manager
            status_messages = [status_result.get(
                'message', 'No message provided.')]
            self.agent_manager.update_status_msg(
                f"Tool {tool_instruct.get('tool')}: {status_messages[0][:100]}...")

            if status_result.get('status') != "200":
                logging.warning(f"Tool execution failed: {status_messages[0]}")
                colored_print(f"Tool failed: {status_messages[0]}", Fore.RED)
                current_prompt.append({
                    'role': 'user',
                    'content': f"Tool execution failed.\nInstruction:\n```json\n{json.dumps(tool_instruct, indent=2)}\n```\nError:\n{status_messages[0]}\n\nPlease correct the tool instruction or parameters and try again."
                })
                retries += 1
                continue  # Retry getting instruction/executing
            else:
                colored_print(
                    f"Tool executed successfully. Result: {status_messages[0]}", Fore.GREEN)
                final_prompt = current_prompt.copy()
                final_prompt.append({
                    'role': 'user',
                    'content': f"Tool execution successful.\nInstruction:\n```json\n{json.dumps(tool_instruct, indent=2)}\n```\nResult:\n{status_messages[0]}\n\nProvide a response summarizing the result or indicating the next step."
                })
                final_response = run_inference(
                    final_prompt, scratchpad_widget, root, self.model_name)
                current_prompt.append(
                    {'role': 'assistant', 'content': final_response})
                return final_response, tool_instruct, status_messages, current_prompt  # Success

        logging.error("Tool use failed after maximum retries.")
        return ("Tool use failed after maximum retries.", tool_instruct, ["Max retries reached."], current_prompt)

    async def code_use(self, base_prompt: List[dict], scratchpad_widget: Any, root: Any) -> Tuple[str, List[str], str, List[dict]]:
        """Handles the process of generating, executing, and responding to Python code use."""
        retries = 0
        current_prompt = base_prompt
        code_script: List[str] = []
        status_message: str = "Code use not attempted."

        while retries < MAX_RETRIES:
            logging.info(
                f"--- Code Use Step (Attempt {retries + 1}/{MAX_RETRIES}) ---")
            raw_response = run_inference(
                current_prompt, scratchpad_widget, root, self.model_name)

            try:
                extracted_blocks = self.extract_code_blocks(
                    raw_response, 'python')
                if not extracted_blocks:
                    raise ValueError("No Python code blocks found.")
                code_script = ["\n".join(extracted_blocks)]

            except ValueError as e:
                logging.warning(f"Code extraction failed: {e}")
                current_prompt = self._build_correction_prompt(
                    current_prompt, raw_response,
                    f"No valid Python code blocks (```python ... ```) found. Please provide the code. Error: {e}"
                )
                retries += 1
                continue  # Retry generation

            current_prompt.append(
                {'role': 'assistant', 'content': raw_response})

            colored_print(
                f"Executing Python Code:\n```python\n{code_script[0][:200]}...\n```", Fore.GREEN)
            status_result = execute_python_code(
                "".join(code_script))  # Execute the joined script
            status_message = status_result.get(
                'message', 'No message provided.')
            self.agent_manager.set_generated_code(
                "".join(code_script))  # For display in Python mode
            self.agent_manager.update_status_msg(
                f"Python: {status_message[:100]}...")  # Update visual status

            if status_result.get('status') != "200":
                logging.warning(f"Code execution failed: {status_message}")
                colored_print(f"Code failed: {status_message}", Fore.RED)
                current_prompt.append({
                    'role': 'user',
                    'content': f"Code execution failed.\nCode:\n```python\n{''.join(code_script)}\n```\nError:\n{status_message}\n\nPlease correct the code and try again."
                })
                retries += 1
                continue  # Retry generation/execution
            else:
                colored_print(
                    f"Code executed successfully. Result: {status_message}", Fore.GREEN)
                final_prompt = current_prompt.copy()
                final_prompt.append({
                    'role': 'user',
                    'content': f"Code execution successful.\nCode:\n```python\n{''.join(code_script)}\n```\nResult:\n{status_message}\n\nProvide a response summarizing the result or indicating the next step."
                })
                final_response = run_inference(
                    final_prompt, scratchpad_widget, root, self.model_name)
                current_prompt.append(
                    {'role': 'assistant', 'content': final_response})
                return final_response, code_script, status_message, current_prompt  # Success

        logging.error("Code use failed after maximum retries.")
        return ("Code use failed after maximum retries.", code_script, "Max retries reached.", current_prompt)

    async def decide_execution(self, text_prompt: dict, output_widget: Any,
                               scratchpad_widget: Any, root: Any, full_prompt: str) -> Tuple[str, str]:
        """Entry point for agent execution based on a user prompt."""
        self.full_prompt = full_prompt
        self.agent_executor.model_name = self.model_var.get()
        base_prompt = load_message_template('base', self.summary)
        base_prompt.append(text_prompt)
        return await self.agent_execution(base_prompt, output_widget, scratchpad_widget, root)

    @staticmethod
    def extract_code_blocks(text: str, language: str) -> List[str]:
        """Extracts code blocks for a specified language, handling optional language labels."""
        pattern = rf"```{re.escape(language)}\s*\n(.*?)\n```|```\n(.*?)\n```"
        try:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            blocks = [block for match in matches for block in match if block]
            if not blocks:
                pattern_any = r"```(?:\w*\s*)?\n(.*?)\n```"
                matches_any = re.findall(pattern_any, text, re.DOTALL)
                if matches_any:
                    logging.warning(
                        f"Found code blocks but language '{language}' mismatch or missing. Using generic blocks.")
                    blocks = [block for block in matches_any if block]

            if not blocks:
                logging.warning(
                    f"No code blocks found for language '{language}' or generic ``` blocks.")

            return blocks
        except Exception as e:
            logging.error(f"Error extracting code blocks: {e}")
            return []
