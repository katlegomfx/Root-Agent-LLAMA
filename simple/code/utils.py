import json
import os
import re
import sys
from typing import Dict, List, Union
from colorama import Fore, Style
from simple.code.system_prompts import MD_HEADING

ESC_LIKE_PATTERN = re.compile(r'(?:←)?\[\d+m')
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


import json
import re
from typing import Dict, List, Union

def extract_json_block(text: str) -> Union[Dict, List, str]:
    """
    Extracts and returns the first valid JSON object or array found in the text.
    It handles:
      - Code blocks labeled as JSON on the same line, e.g. ```json\n{...}\n```
      - Code blocks labeled as JSON on a new line, e.g. ```
        json
        {...}
        ```
      - Code blocks without "json" label, e.g. ```\n{...}\n```
      - No code blocks at all, in which case it tries to parse the entire text.

    Raises:
        ValueError: If no valid JSON block is found.
    """

    # 1) Try code blocks labeled as JSON on the same or next line
    #    Examples:
    #       ```json\n{...}\n```
    #       ```\njson\n{...}\n```
    # We allow optional whitespace around "json" and also allow it to be on the same line or the next line.
    json_labeled_pattern = re.compile(
        r"```(?:\s*\n\s*)?(?:json\s*)(?:\n|\r\n)(.*?)```",
        flags=re.DOTALL | re.IGNORECASE
    )

    matches = json_labeled_pattern.findall(text)
    if matches:
        for block in matches:
            try:
                return json.loads(block.strip())
            except json.JSONDecodeError:
                continue  # Try the next match if parsing fails

    # 2) Fallback to any triple-backtick code block (no "json" label).
    #    Example:
    #       ```\n{...}\n```
    generic_pattern = re.compile(
        r"```(.*?)```",
        flags=re.DOTALL
    )
    matches = generic_pattern.findall(text)
    if matches:
        for block in matches:
            try:
                return json.loads(block.strip())
            except json.JSONDecodeError:
                continue  # Try the next match if parsing fails

    # 3) Lastly, attempt to parse the entire text as JSON.
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass  # Parsing the entire text failed

    # If we reach here, no valid JSON was found.
    raise ValueError("No valid JSON block found in the text.")

