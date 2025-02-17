# Bot\build\code\llm\llm_client.py
from colorama import Fore, Style
import ollama
import time
import json
import os
import traceback
from datetime import datetime
from typing import List, Dict, Any

from ollama import AsyncClient
from huggingface_hub import hf_hub_download

from Bot.build.code.cli.cli_helpers import colored_print, strip_model_escapes
from Bot.build.code.io_utils import get_next_filename_index, write_content_to_file

from Bot.build.code.tasks.base_execute import execute_tool
from Bot.build.code.llm.extract import extract_code

from Bot.build.code.session.constants import (
    code_prefix,
    assistant_prefix,
    ai_code_path,
    ai_errors_path,
    ai_results_path,
    anonymised, error_file,
    gen_ai_path,
    MODELS_PATH,
    model_map,
)





def inferencing(messages: List[Dict[str, str]], model_id: str = 'DeepBabySeek') -> str:
    if model_id not in ollama.list()['models']:
        model_info, model_basename = model_map[model_id]
        model_path = hf_hub_download(
            repo_id=model_info,
            filename=model_basename,
            cache_dir=MODELS_PATH,
        )
        print(model_id)
        print(model_path)
        input("model_path")

        modelfile = f'''
FROM {model_path}
# set the temperature to 1 [higher is more creative, lower is more coherent]
PARAMETER temperature 2
'''

        ollama.create(model=model_id, modelfile=modelfile)

    # assistant_response = ''
    # # Directly iterate over the async iterator returned by AsyncClient().chat(...)
    # client = AsyncClient()
    # response_generator = await client.chat(model=model_id, messages=messages, stream=True)
    # async for part in response_generator:
    #     section = part['message']['content']
    #     print(section, end='', flush=True)
    #     assistant_response += section
    # print()
    # return assistant_response

    stream = ollama.chat(
        model=model_id,
        messages=messages,
        stream=True,
    )

    response = ''

    for chunk in stream:
        text = chunk['message']['content']
        print(text, end='', flush=True)
        response += text

    print()
    return response

# print(inference('code', 'How to do ML in python?'))


async def chat(messages: List[Dict[str, str]], model: str = 'llama3.2') -> str:
    """
    Sends a list of messages to the AsyncClient and streams the assistant response.
    Conditionally prints the assistant output in color if in a TTY.
    """
    print(f"#"*75)
    assistant_response = ''
    client = AsyncClient()
    response_generator = await client.chat(model=model, messages=messages, stream=True)
    async for part in response_generator:
        section = part['message']['content']
        section_clean = strip_model_escapes(section)
        colored_print(section_clean, color=Fore.YELLOW, end='', flush=True)
        assistant_response += section
    print()
    return assistant_response


async def infer(messages: List[Dict[str, str]], model: str = 'llama3.2'):
    start_time = time.time()
    response = await chat(messages)
    time_taken = time.time() - start_time

    # Get current timestamp in two formats:
    # One for the top of the markdown, and one for the filename.
    timestamp_md = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_file = datetime.now().strftime('%Y%m%d%H%M%S')

    # Build Markdown content
    md_content = f"# {timestamp_md}\n\n"  # Time at the top as a heading
    md_content += "## Request Info\n\n"
    md_content += "### Input\n"
    md_content += f"**Instructions:** {messages[0]['content']}\n\n"
    md_content += f"**Prompt:** {messages[-1]['content']}\n\n"
    md_content += "### Output\n"
    md_content += f"{response}\n\n"
    md_content += "### Processing\n"
    md_content += f"Time taken: {time_taken:.2f} seconds\n"

    # Determine file name and write the Markdown content
    number_of_files = get_next_filename_index(
        ai_results_path, assistant_prefix)
    file_path = os.path.join(gen_ai_path, ai_results_path, f'{
                             assistant_prefix}_{timestamp_file}.md')
    write_content_to_file(md_content, file_path)


def see(messages: List[Dict[str, Any]]) -> str:
    # messages = [{
    #     'role': 'user',
    #     'content': 'What is in this image?',
    #     'images': ['image.jpg']
    # }]
    response = ollama.chat(
        model='llama3.2-vision',
        messages=messages,
        stream=True
    )
    assistant_response = ''
    for chunk in response:
        section = chunk['message']['content']
        print(section, end='', flush=True)
        assistant_response += section
    print()
    return response


async def process_user_messages_with_model(messages: List[Dict[str, str]], tool_use: bool = False, execute: bool = False, model: str = 'llama3.2') -> str:
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
        assistant_response = await infer(messages, model)

        executions = []

        py_codes = []

        tsx_codes = []
        ts_codes = []
        jsx_codes = []
        js_codes = []

        if tool_use:
            tool_codes = extract_code(assistant_response, language='json')

            if len(tool_codes) == 0:
                tool_codes = extract_code(assistant_response, language='bash')
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
                        if not result or "Error" in result:
                            # Tool failed or returned an error
                            observation_msg = {
                                'role': 'system',
                                'content': f"Tool Execution Failed. Error info: {result}"
                            }
                            # Insert the observation into the conversation chain
                            messages.append(observation_msg)
                            # Re-run the model with an additional user/system prompt:
                            correction_prompt = {
                                'role': 'user',
                                'content': (
                                    "The previous tool call failed. Please correct the tool instruction or reason out a fix."
                                    "If the tool can’t be fixed, provide a final message."
                                )
                            }
                            messages.append(correction_prompt)
                            # Then call the model again
                            corrected_response = await infer(messages)
                        executions.append(result)

                        evaluation_prompt = {
                            'role': 'system',
                            'content': "Self-evaluation: Is this final answer correct or does it need further correction?"
                        }
                        messages.append(evaluation_prompt)
                        evaluation_result = await infer(messages)

                        # If the agent says it's correct, proceed.
                        # If not, let it fix itself or disclaim the limitation.

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
            javascript_codes = extract_code(assistant_response, 'javascript')
            for code in javascript_codes:
                number_of_files = get_next_filename_index(
                    os.path.join(ai_code_path, 'nextjs'), ".js")
        return assistant_response

    except Exception as e:
        error_content = 'An error ocurred:\n'
        error_content += traceback.format_exc().replace(anonymised, '')
        write_content_to_file(
            error_content, os.path.join(gen_ai_path, ai_errors_path, error_file))

        print(f'An error ocurred:\n{e}')
