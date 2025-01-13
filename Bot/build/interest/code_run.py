### building\code\code_run.pyimport logging
import os
import ast
import shlex
import subprocess
from building import file_system, run_command  # nopep

BASE_DIR = os.path.abspath("./projects")
ALLOWED_COMMANDS = {'ls', 'echo', 'grep', 'py', 'npm', 'pip'}

def clean_string(the_string):
    ### Assuming your string cleaning logic is correct    start_indexing = the_string.find('{')
    end_indexing = the_string.rfind('}')
    working_str = the_string[start_indexing:end_indexing + 1]
    final_str = working_str.replace('\n', '').replace('`', '')
    return final_str

def extract_dictionaries_from_string(input_string):
    clean_test_string = clean_string(input_string)
    dictionaries = []
    ### Attempt to convert the cleaned string to an actual dictionary    try:
        ### Ensure clean_test_string is properly formatted for literal_eval        if clean_test_string.startswith('{') and clean_test_string.endswith('}'):
            dictionary = ast.literal_eval(clean_test_string)
            dictionaries.append(dictionary)
        else:
            print(f"String format error: {clean_test_string}")
    except (ValueError, SyntaxError) as e:
        print(
            f"Could not convert '{clean_test_string}' to dictionary: {e}")

    return dictionaries if dictionaries else []

def is_safe_path(path):
    """Validate paths to ensure they are under the BASE_DIR and prevent directory traversal."""
    try:
        full_path = os.path.abspath(os.path.join(BASE_DIR, path))
        logging.debug(f"Checking path: {full_path}")
        if not full_path.startswith(BASE_DIR):
            logging.warning(
                f"Attempt to access outside the base directory: {full_path}")
            return False
        logging.info(f"Accessing path: {full_path}")
        return True
    except OSError as e:
        logging.error(f"Invalid path operation: {e}")
        return False

def remove_function_keys(original_dict):
    new_dict = {}
    for key, value in original_dict.items():
        ### Copy the dictionary if it's a sub-dictionary        if isinstance(value, dict):
            new_sub_dict = {
                sub_key: sub_value for sub_key,
                sub_value in value.items() if sub_key != 'function'}
            new_dict[key] = new_sub_dict
    return new_dict

def create_file(file_path, content):
    """
    Create a new file at a specified path with given content.
    Expected Arguments: {'file_path': './path/', 'content': 'file content'}
    """
    if not is_safe_path(file_path):
        logging.error("Invalid path. Directory traversal is not allowed.")
        return False, "Invalid path"

    file_path = os.path.join(BASE_DIR, file_path)
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        logging.info(f"File '{file_path}' created successfully")
        return True, f"File '{file_path}' created successfully"
    except IOError as e:
        logging.error(f"Failed to create file '{file_path}': {e}")
        return False, f"Failed to create file '{file_path}'. Reason: {e}"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False, f"Unexpected error occurred. Reason: {e}"

def functions_string(processed_dict):
    processed_str = remove_function_keys(processed_dict)
    final_str = ''
    for key, value in processed_str.items():
        if key not in ["standard_response", "is_safe_path"]:
            final_str += f"name: {key}"
            final_str += f"{value['docstring']}\n"
    return f"{final_str}"

def get_functions_from_module(module):
    function_dict = {
        attribute_name: {"function": attribute, "docstring": attribute.__doc__}
        for attribute_name in dir(module)
        if callable((attribute := getattr(module, attribute_name))) and
        isinstance(attribute, type(lambda: None)) and
        attribute.__module__ == module.__name__
    }
    return function_dict

def run_command_in(command_line: str) -> tuple:
    """Execute system commands safely with detailed error handling and timeouts."""
    try:
        command_parts = shlex.split(command_line)
        if command_parts[0] not in ALLOWED_COMMANDS:
            raise ValueError(f"Command '{command_parts[0]}' is not permitted.")

        result = subprocess.run(command_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)

        if result.returncode != 0:
            logging.error(f"Command '{command_line}' failed with error: {result.stderr}")
            return False, result.stderr
        return True, result.stdout
    except subprocess.TimeoutExpired:
        logging.error("Command execution timed out.")
        return False, "Command timed out."
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{command_line}' failed: {e}")
        return False, f"Command failed: {e}"
    except ValueError as e:
        logging.error(f"Invalid command: {e}")
        return False, f"Invalid command: {e}"
    except Exception as e:
        logging.error(f"Unexpected error during command execution: {e}")
        return False, f"Unexpected error: {e}"

def create_directory(path):
    """Create directory safely and handle exceptions."""
    safe_path = os.path.join(BASE_DIR, path)
    if not is_safe_path(safe_path):
        logging.error(f"Invalid path: {safe_path}")
        return False, "Invalid path. Directory traversal is not allowed."

    try:
        os.makedirs(safe_path, exist_ok=True)
        logging.info(f"Directory created: {safe_path}")
        return True, f"Directory '{safe_path}' created successfully"
    except OSError as e:
        logging.error(f"Failed to create directory: {e}")
        return False, f"Failed to create directory '{safe_path}'. Reason: {e}"

file_system_functions = get_functions_from_module(
    file_system)
run_command_functions = get_functions_from_module(
    run_command)
file_system_functions_string = functions_string(
    file_system_functions)
run_command_functions_string = functions_string(
    run_command_functions)
print_see = "####################"*3
function_map = {**file_system_functions, **run_command_functions}

def extract_command_or_code_with_type(api_response):
    """
    Extracts commands or code snippets and their types from a given API response text.
    The API response is expected to contain code blocks marked by triple backticks.
    This function identifies the type of each code block (e.g., bash, python, javascript) and returns them.
    """
    ### Split the response into lines    lines = api_response.split('\n')

    ### Initialize variables to hold the extracted code, its type, and a list to collect all code blocks    code_blocks = []

    ### Variables for the current code block    current_code = ''
    current_type = ''
    collecting = False

    ### Loop through each line    for line in lines:
        ### Check if the line indicates the start of a code block        if line.strip().startswith('```') and current_code == '':
            ### Extract the code type from the line            current_type = line.strip()[3:]
            base_lines = [
                'json',
                'bash',
                'shell',
                'sh',
                'python',
                'py',
                'javascript',
                'js',
            ]
            if current_type.lower() in base_lines:
                collecting = True
            else:
                collecting = False

        elif line.strip() == '```' and current_code != '':
            ### Append the current code block and its type to the list            code_blocks.append((current_code.strip(), current_type))
            current_code, current_type = '', ''  # Reset for the next block
            collecting = False
        else:
            ### Accumulate code lines            if collecting:
                base_lines = [
                    '```json',
                    '```shell',
                    '```sh',
                    '```bash',
                    '```python',
                    '```py',
                    '```javascript',
                    '```js',
                ]
                current_code += line + '\n' if line.lower() not in base_lines else ""

    return code_blocks

def execute_function_from_response(clean_response):
    """
    Executes a function based on the cleaned response containing function names and their arguments.
    """
    func_name = clean_response.get('name')
    if not func_name or func_name not in function_map:
        return False, f"Function {func_name} not recognized."

    func = function_map[func_name]
    args = clean_response.get('arguments', {})

    try:
        result = func['function'](**args)
        return True, result
    except TypeError as e:
        logging.error(f"Failed to execute {func_name}: {e}")
        return False, str(e)

def process_execute(input_response):
    """run a code from string"""
    response_cleaned = extract_command_or_code_with_type(
        input_response)
    run_response = None  # Initialize to prevent UnboundLocalError

    base_lines = {
        'json', 'bash', 'shell', 'sh', 'python', 'py', 'javascript', 'js'
    }

    for code, code_type in response_cleaned:
        if code_type.lower() in base_lines:
            if 'python' in code_type.lower():
                create_file('base.py', code)
                run_response = run_command_in('py projects/base.py')
            elif code_type.lower() in {'bash', 'shell', 'sh'}:
                run_response = run_command_in(code)
            elif code_type.lower() == 'json':
                print("Ran JSON")
                clean_response = extract_dictionaries_from_string(
                    code)
                for string_dict in clean_response:
                    run_response = execute_function_from_response(
                        string_dict)
        else:
            print("Code type not supported:", code_type)

    if run_response is None:
        run_response = (False, "No valid code block executed.")

    print("Execution Result:", run_response)
    return run_response
