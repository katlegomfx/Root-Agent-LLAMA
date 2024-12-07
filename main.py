import asyncio
import re
from ollama import AsyncClient
import traceback
import time
import os
import json
import subprocess
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

assistant_prefix = 'assistant_resposne'
code_prefix = 'assistant_code'

ai_code_path = 'gen_ai_code'
ai_errors_path = 'gen_ai_errors'
ai_results_path = 'gen_ai_results'

anonymised = os.getenv('anonymised') if os.getenv('anonymised') else ''

error_file = 'currentError.txt'

os.makedirs(ai_code_path, exist_ok=True)
os.makedirs(ai_errors_path, exist_ok=True)
os.makedirs(ai_results_path, exist_ok=True)


def read_file_content(path: str) -> str:
    """Reads and returns the entire content of the given file path as a string."""
    with open(path, 'r') as f:
        return "".join(f.readlines())


def write_content_to_file(content: str, path: str) -> None:
    """Writes the given content to a file at the specified path."""
    with open(path, 'w') as f:
        f.write(content)


def get_next_filename_index(directory: str, prefix: str) -> int:
    """
    Returns the next available file index in the given directory for files 
    starting with the given prefix.
    """
    return len([item for item in os.listdir(directory) if item.startswith(prefix)])


async def chat(messages: List[Dict[str, str]]) -> str:
    """
    Sends a list of messages to the AsyncClient and streams the assistant response.
    
    Parameters:
        messages (List[Dict[str, str]]): A list of messages where each message is a dict with 'role' and 'content' keys.

    Returns:
        str: The complete assistant response as a string.
    """
    assistant_response = ''
    async for part in await AsyncClient().chat(model='llama3.2', messages=messages, stream=True):
        section = part['message']['content']
        print(section, end='', flush=True)
        assistant_response += section
    print()
    return assistant_response


def extract_code(text: str, language: str = 'python') -> list[str]:
    """
    Extracts code blocks of the specified programming language from the given text.
    
    Parameters:
        text (str): The full text possibly containing code blocks.
        language (str): The language to look for in triple-backtick code fences.

    Returns:
        List[str]: A list of code block strings.
    """
    triple_backticks = '`'*3
    base_pattern = rf'{triple_backticks}{language}(.*?){triple_backticks}'
    code_blocks = re.findall(base_pattern, text, re.DOTALL)
    return code_blocks


def process_user_messages_with_model(messages: List[Dict[str, str]], tool_use: bool = False, execute: bool = False) -> None:
    """
    Processes user messages with the Ollama model. Depending on the parameters, it may extract code blocks 
    (either JSON for tools or Python code), run commands, and store results and metadata.

    Parameters:
        messages (List[Dict[str, str]]): A list of messages for the model, each message containing a role and content.
        tool_use (bool): If True, treats the response as a JSON tool instruction block.
        execute (bool): If True, executes the code instructions in the JSON response (not yet implemented).

    Returns:
        None
    """
    try:
        start_time = time.time()
        assistant_response = asyncio.run(chat(messages))
        time_taken = time.time() - start_time

        if tool_use:
            codes = extract_code(assistant_response, language='json')
            for code in codes:
                json_instruct = json.loads(code)
                print(json.dumps(json_instruct, indent=4))

                if execute:
                    # TODO
                    pass

            input('correct?')

        else:
            codes = extract_code(assistant_response)
            number_of_files = get_next_filename_index(ai_code_path, code_prefix)
            for code in codes:
                write_content_to_file(code, os.path.join(
                    ai_code_path, f'{code_prefix}{number_of_files}.py'))

        request_info = {
            'input': {
                'instructions': messages[0]['content'],
                'prompt': messages[-1]['content']
            },
            'output': {
                'response': assistant_response,
                'code': codes
            },
            'processing': {
                'time_taken': time_taken
            }
        }
        json_request_info = json.dumps(request_info, indent=4)

        number_of_files = get_next_filename_index(ai_results_path, assistant_prefix)
        write_content_to_file(json_request_info, os.path.join(
            ai_results_path, f'{assistant_prefix}{number_of_files}.json'))

    except Exception as e:
        error_content = 'An error ocurred:\n'
        error_content += traceback.format_exc().replace(anonymised, '')
        write_content_to_file(
            error_content, os.path.join(ai_errors_path, error_file))

        print(f'An error ocurred:\n{e}')


def run_bash_command(command: str) -> str:
    """
    Runs a bash command and returns its output.

    Parameters:
        command (str): The bash command to be executed.

    Returns:
        str: The output of the executed bash command.
    """
    try:
        result = subprocess.run(command, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}"


def init_messages() -> (List[Dict[str, str]], List[Dict[str, str]]): # type: ignore
    """
    Initializes the message contexts for both general messages and tool messages.

    Returns:
        (List[Dict[str, str]], List[Dict[str, str]]): A tuple containing two lists of messages.
    """
    base_general_messages = [
        {'role': 'system', 'content': 'You are an expert python developer'}
    ]

    hard_coded = f"# You are an AI system, running on a windows machine"
    hard_coded += f"""
# Avaliable Tool:
## Name: 
{run_bash_command.__name__}
## Doc: 
{run_bash_command.__doc__}
## Usage:
- Provide a JSON response wrapped in triple backticks and json
- The response should contain the tool name and parameter values
- {{tool: <name>, parameters: <[values]>}}
"""
    base_tool_messages = [
        {"role": 'system', "content": hard_coded}
    ]

    return base_general_messages, base_tool_messages


def main() -> None:
    """
    The main entry point of the CLI application. Continuously prompts the user for input, 
    processes commands and integrates with the Ollama model and tools.
    """
    messages, tool_messages = init_messages()

    while True:
        user_input = input('\n> ')

        if not user_input or user_input.startswith('exit'):
            if user_input.startswith('exit'):
                print('Goodbye')
            break

        if user_input.startswith('clear'):
            messages, tool_messages = init_messages()

        elif user_input.startswith('self'):
            # Gather anfo
            base_code = read_file_content('main.py')
            user_request = user_input.replace('self ', '')
            # Create prompt
            prompt = f'# Considering the following: \n\n{base_code}\n\n# {user_request})'
            # Compile prompt
            messages.append({'role': 'user', 'content': prompt})
            process_user_messages_with_model(messages)

        elif user_input.startswith('fix'):
            # Gather info
            base_code = read_file_content('main.py')
            error_code = read_file_content(
                os.path.join(ai_errors_path, error_file))
            user_request = user_input.replace('fix ', '')
            # Create prompt
            prompt = f'# Considering the following:\n\n{base_code}\n\n# What modifications need to be made in order to address the error:\n\n{error_code}'
            # Compile prompt
            messages.append({'role': 'user', 'content': prompt})
            process_user_messages_with_model(messages)

        elif user_input.startswith('tool'):
            user_input = user_input.replace('tool ', '')
            prompt = user_input
            tool_messages.append({'role': 'user', 'content': prompt})
            process_user_messages_with_model(tool_messages, tool_use=True)

        else:
            # Create prompt
            prompt = user_input
            # Compile prompt
            messages.append({'role': 'user', 'content': prompt})
            process_user_messages_with_model(messages)


if __name__ == "__main__":
    main()
