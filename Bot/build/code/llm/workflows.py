# Bot\build\code\llm\workflows.py
from ast import Dict
import asyncio
import json
from typing import List

from Bot.build.code.llm.extract import extract_code
from Bot.build.code.llm.llm_client import chat
from Bot.build.code.tasks.base_execute import execute_code, execute_tool
from Bot.build.code.session.constants import (
    code_prefix,
    assistant_prefix,
    summary_prefix,
    ai_code_path,
    ai_results_path,
    ai_history_path,
    ai_errors_path,
    ai_summaries_path,
    binary_answer,
    anonymised, error_file,
    triple_backticks,
    md_heading,
    gen_ai_path,
    MODELS_PATH,
    model_map
)

async def tool_use(base_prompt):
    """
    Main loop for:
     1. Asking the model for JSON-based tool instructions
     2. Extracting them from triple backtick code fences
     3. Executing them
     4. Handling success/failure and re-asking if needed
    """
    base_response = await asyncio.gather(chat(base_prompt))
    base_text = "".join(base_response)
    tool_script = extract_code(base_text, 'json')
    if not tool_script:
        correction_prompt = base_prompt.copy()
        correction_prompt.append(
            {
                'role': 'assistant',
                'content': json.dumps(base_response)
            }
        )
        correction_prompt.append(
            {
                'role': 'user',
                'content': "Remember to wrap the instruction in triple backticks and specify 'json'."
            }
        )
        return await tool_use(correction_prompt)
    status_messages = []
    for code_snippet in tool_script:
        json_instruct = json.loads(code_snippet)
        if isinstance(json_instruct, List):
            json_instruct = json_instruct[0]
        elif isinstance(json_instruct, str):

            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {
                    'role': 'assistant',
                    'content': json.dumps(base_response)
                }
            )
            correction_prompt.append(
                {
                    'role': 'user',
                    'content': "Remember to wrap the instruction in triple backticks and specify 'json'. with an object containing tool and parameters."
                }
            )
            return await tool_use(correction_prompt)
        status_message = execute_tool(json_instruct)

        if status_message['status'] != "200":
            new_prompt = base_prompt.copy()
            new_prompt.append(
                {
                    'role': 'assistant',
                    'content': json.dumps(base_response)
                }
            )
            new_prompt.append(
                {
                    'role': 'user',
                    'content': (
                        f"{md_heading} Generated tool instruction:\n\n"
                        + json.dumps(tool_script)
                        + f"\n\n{md_heading} Execution result:\n\n"
                        + status_message['message']
                        + f"\n\n{md_heading} Fix the above error"
                    )
                }
            )
            return await tool_use(new_prompt)
        else:
            base_prompt.append(
                {
                    'role': 'assistant',
                    'content': json.dumps(base_response)
                }
            )
            status_messages.append(status_message)

        final_prompt = base_prompt.copy()
        final_prompt.append(
            {
                'role': 'user',
                'content': (
                    f"{md_heading} Generated tool instruction:\n\n"
                    + code_snippet
                    + f"\n\n{md_heading} Execution result:\n\n"
                    + status_message['message']
                )
            }
        )
        final_response = await asyncio.gather(chat(final_prompt))
        final_text = "".join(final_response)
        final_prompt.append({'role': 'assistant', 'content': final_text})

        return final_response, tool_script, status_messages, final_prompt

async def code_use(base_prompt):
    """
    Main loop for:
     1. Asking the model for Python code
     2. Extracting it from triple backtick code fences
     3. Executing it
     4. Handling success/failure and re-asking if needed
    """
    base_response = await asyncio.gather(chat(base_prompt))
    base_text = "".join(base_response)
    code_script = extract_code(base_text, 'python')

    status_message = execute_code("".join(code_script))
    if status_message['status'] != "200":
        new_prompt = base_prompt.copy()
        new_prompt.append({'role': 'assistant', 'content': base_text})
        new_prompt.append(
            {
                'role': 'user',
                'content': (
                    f"{md_heading} Generated code:\n\n"
                    + "".join(code_script)
                    + f"\n\n{md_heading} Execution result:\n\n"
                    + status_message['message']
                )
            }
        )
        return await tool_use(new_prompt)
    else:
        base_prompt.append({'role': 'assistant', 'content': base_text})
        base_prompt.append(
            {
                'role': 'user',
                'content': (
                    f"{md_heading} Generated code:\n\n"
                    + "".join(code_script)
                    + f"\n\n{md_heading} Execution result:\n\n"
                    + status_message['message']
                )
            }
        )
        final_response = await asyncio.gather(chat(base_prompt))
        final_text = "".join(final_response)
        base_prompt.append({'role': 'assistant', 'content': final_text})
        return final_response, code_script, status_message, base_prompt

async def accomplished_request(base_prompt):
    base_response = await asyncio.gather(chat(base_prompt))
    base_text = "".join(base_response)
    use_script = extract_code(base_text, 'json')
    results = []
    for code_snippet in use_script:
        json_instruct = json.loads(code_snippet)

        if 'use' in json_instruct and json_instruct['use'].lower() in ['yes']:
            base_prompt.append(
                {
                    'role': 'assistant',
                    'content': json.dumps(base_response)
                }
            )
            result = json_instruct["use"].lower()
            results.append(result)
        if 'use' in json_instruct and json_instruct['use'].lower() in ['yes']:
            base_prompt.append(
                {
                    'role': 'assistant',
                    'content': json.dumps(base_response)
                }
            )
            result = json_instruct["use"].lower()
            results.append(result)

    return results

async def decide_execution(base_prompt):
    base_response = await asyncio.gather(chat(base_prompt))
    base_text = "".join(base_response)
    use_script = extract_code(base_text, 'json')

    if not use_script:
        correction_prompt = base_prompt.copy()
        correction_prompt.append(
            {
                'role': 'assistant',
                'content': base_text
            }
        )
        correction_prompt.append(
            {
                'role': 'user',
                'content': "Remember to wrap the instruction in triple backticks and specify 'json'. (start response with ```json)"
            }
        )
        return await decide_execution(correction_prompt)

    for code_snippet in use_script:
        json_instruct = json.loads(code_snippet)
        if isinstance(json_instruct, List):
            json_instruct = json_instruct[0]
        elif isinstance(json_instruct, str):
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {
                    'role': 'assistant',
                    'content': json.dumps(base_response)
                }
            )
            correction_prompt.append(
                {
                    'role': 'user',
                    'content': "Remember to wrap the instruction in triple backticks and specify 'json'. with an object containing the key 'use' and a 'value' either python or json."
                }
            )
            return await decide_execution(correction_prompt)

        if 'use' in json_instruct and json_instruct['use'].lower() in ['python', 'tool']:
            base_prompt.append(
                {
                    'role': 'assistant',
                    'content': json.dumps(base_response)
                }
            )
            result = json_instruct["use"].lower()
            return result
        else:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {
                    'role': 'assistant',
                    'content': json.dumps(base_response)
                }
            )
            correction_prompt.append(
                {
                    'role': 'user',
                    'content': "Please produce a JSON object with 'use' key and python or tool as 'value'."
                }
            )
            return await decide_execution(correction_prompt)
