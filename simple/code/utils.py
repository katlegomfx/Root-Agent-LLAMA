import json
import os
import re
import sys
from typing import Dict, List, Union
from colorama import Fore, Style
from simple.code.system_prompts import MD_HEADING

# Pattern to remove model artifacts (e.g., '←[0m')
ESC_LIKE_PATTERN = re.compile(r'(?:←)?\[\d+m')
# Check if the output supports color.
USE_COLOR = sys.stdout.isatty()


def strip_model_escapes(text: str) -> str:
    """
    Removes model-generated sequences (like '←[0m') that are not true ANSI escapes.
    """
    return ESC_LIKE_PATTERN.sub('', text)


def colored_print(text: str, color: str = Fore.RESET, end: str = "\n", flush: bool = False):
    """
    Prints text in the specified color (if terminal supports it), then resets style.
    """
    if USE_COLOR:
        print(f"{color}{text}{Style.RESET_ALL}", end=end, flush=flush)
    else:
        print(text, end=end, flush=flush)


def get_py_files_recursive(directory: str, exclude_dirs: List[str] = None, exclude_files: List[str] = None) -> List[str]:
    """
    Recursively finds Python files in a directory, excluding specified directories and files.
    """
    if exclude_dirs is None:
        exclude_dirs = ['venv']
    if exclude_files is None:
        exclude_files = []
    py_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py') and file not in exclude_files:
                py_files.append(os.path.join(root, file))
    return py_files


def read_file_content(path: str) -> str:
    """
    Reads and returns the content of a file.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content.replace(f'{MD_HEADING} ', f'{MD_HEADING*2} ')
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return ""


def code_corpus(directory: str) -> List[str]:
    """
    Builds a corpus by reading all Python files in the directory, excluding certain files and folders.
    """
    exclude_files = []
    exclude_dirs = ['interest', 'pyds', 'backup', 'models', 'sdlc',
                    'self_autoCode', 'self_autoCodebase', 'tests', 'to_confirm_tools', 'node_modules', '']
    file_paths = get_py_files_recursive(
        directory, exclude_dirs=exclude_dirs, exclude_files=exclude_files)
    corpus = []
    for file_path in file_paths:
        try:
            text = read_file_content(file_path)
            corpus.append(f'\n{MD_HEADING} {file_path}:\n{text}\n')
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    return corpus


def extract_json_block(text: str) -> Union[Dict, List, str]:
    """
    Extracts and returns the first valid JSON object or array found in the text.
    It searches for JSON blocks within triple backticks (with or without a language label)
    and also attempts to parse the entire text as JSON if no backticks are found.

    Raises:
        ValueError: If no valid JSON block is found.
    """

    # First, try to find JSON within triple backticks (with or without language label)
    pattern = r"```(?:\w*\n)?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    if matches:
        for block in matches:
            try:
                json_obj = json.loads(block.strip())
                return json_obj
            except json.JSONDecodeError:
                continue  # Try the next match if parsing fails

    # If no JSON within backticks was found, attempt to parse the entire text as JSON
    try:
        json_obj = json.loads(text.strip())
        return json_obj
    except json.JSONDecodeError:
        pass  # Parsing the entire text failed

    raise ValueError("No valid JSON block found in the text.")
