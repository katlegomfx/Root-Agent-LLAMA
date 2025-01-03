import time
import json
import os
import traceback
from datetime import datetime
from typing import List, Dict, Any

from ollama import AsyncClient

from Bot.build.code.io_utils import get_next_filename_index, write_content_to_file

from Bot.build.code.tasks.base_execute import execute_tool
from Bot.build.code.llm.extract import extract_code

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
    gen_ai_path
)

async def chat(messages: List[Dict[str, str]]) -> str:
    """Sends a list of messages to the AsyncClient and streams the assistant response."""
    assistant_response = ''
    # Directly iterate over the async iterator returned by AsyncClient().chat(...)
    client = AsyncClient()
    response_generator = await client.chat(model='llama3.2', messages=messages, stream=True)
    async for part in response_generator:
        section = part['message']['content']
        print(section, end='', flush=True)
        assistant_response += section
    print()
    return assistant_response





async def process_user_messages_with_model(messages: List[Dict[str, str]], tool_use: bool = False, execute: bool = False) -> str:
    """
    Processes user messages with the Ollama model. Depending on the parameters, it may extract code blocks 
    (either JSON for tools or Python code), run commands, and store results and metadata.

    Parameters:
        messages (List[Dict[str, str]]): A list of messages for the model, each message containing a role and content.
        tool_use (bool): If True, treats the response as a JSON tool instruction block.
        execute (bool): If True, executes the code instructions in the JSON response (not yet implemented).

    Returns:
        str
    """
    try:
        start_time = time.time()
        assistant_response = await chat(messages)
        time_taken = time.time() - start_time
        executions = []
        if tool_use:
            tool_codes = extract_code(assistant_response, language='json')
            # executions =  []
            for code in tool_codes:
                json_instruct = json.loads(code)
                # print(json.dumps(json_instruct, indent=4))

                if execute:
                    confirm = input(
                        f"Are you sure you want to execute the tool? (y/n): ")
                    while confirm.lower() not in ['y', 'n']:
                        confirm = input("Please enter y or n: ")

                    if confirm.lower() == 'y':
                        # Execute the tool
                        print(f"Executing tool: {json_instruct}")
                        result = execute_tool(json_instruct)
                        executions.append(result)

        else:
            py_codes = extract_code(assistant_response)
            for code in py_codes:
                number_of_files = get_next_filename_index(
                    ai_code_path, code_prefix)
                # Write the code to a file
                write_content_to_file(code, os.path.join(
                    gen_ai_path, ai_code_path, f'{code_prefix}{number_of_files}.py'))
                # Execute the code
                if execute:
                    confirm = input(
                        f"Are you sure you want to execute the code? (y/n): ")
                    while confirm.lower() not in ['y', 'n']:
                        confirm = input("Please enter y or n: ")

                    if confirm.lower() == 'y':
                        # Execute the code
                        print(f"Executing code: {code}")
                        result = execute_tool({
                            'tool': 'execute_bash_command',
                            'parameters': f"py -c {code}"
                        })
                        executions.append(result)

            tsx_codes = extract_code(assistant_response, 'tsx')
            for code in tsx_codes:
                number_of_files = get_next_filename_index(
                    os.path.join(ai_code_path, 'nextjs'), ".tsx")
            ts_codes = extract_code(assistant_response, 'ts')
            for code in ts_codes:
                number_of_files = get_next_filename_index(
                    os.path.join(ai_code_path, 'nextjs'), ".ts")
            jsx_codes = extract_code(assistant_response, 'jsx')
            for code in jsx_codes:
                number_of_files = get_next_filename_index(
                    os.path.join(ai_code_path, 'nextjs'), ".jsx")
            js_codes = extract_code(assistant_response, 'js')
            for code in js_codes:
                number_of_files = get_next_filename_index(
                    os.path.join(ai_code_path, 'nextjs'), ".js")

        request_info = {
            'input': {
                'instructions': messages[0]['content'],
                'prompt': messages[-1]['content']
            },
            'output': {
                'response': assistant_response,
                'code': py_codes,
            },
            'processing': {
                'time_taken': time_taken,

            }
        }

        if executions != []:
            request_info['processing']['executions'] = executions
            assistant_response += "\n".join(executions)

        json_request_info = json.dumps(request_info, indent=4)

        number_of_files = get_next_filename_index(
            ai_results_path, assistant_prefix)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        write_content_to_file(json_request_info, os.path.join(gen_ai_path,
                                                              ai_results_path, f'{assistant_prefix}_{timestamp}.json'))

        return assistant_response

    except Exception as e:
        error_content = 'An error ocurred:\n'
        error_content += traceback.format_exc().replace(anonymised, '')
        write_content_to_file(
            error_content, os.path.join(gen_ai_path, ai_errors_path, error_file))

        print(f'An error ocurred:\n{e}')
