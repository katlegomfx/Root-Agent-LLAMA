import os
import re
import sys
from typing import List
from colorama import Fore, Style


from simple.code.system_prompts import MD_HEADING

ESC_LIKE_PATTERN = re.compile(r'(←\[\d+m)')
USE_COLOR = sys.stdout.isatty()

def strip_model_escapes(text: str) -> str:
    """
    Removes leftover model-generated sequences like '←[0m' or '←[33m' 
    that are not real ANSI escapes but textual artifacts.
    """
    return ESC_LIKE_PATTERN.sub('', text)


def colored_print(text: str, color: str = Fore.RESET, end: str = "\n", flush: bool = False):
    """
    Prints the given text in the specified color, resetting style afterward.
    Only prints color codes if USE_COLOR is True.
    """
    if USE_COLOR:
        print(f"{color}{text}{Style.RESET_ALL}", end=end, flush=flush)
    else:
        print(text, end=end, flush=flush)

def get_py_files_recursive(directory: str, exclude_dirs: List[str] = None, exclude_files: List[str] = None) -> List[str]:
    """
    Recursively searches for Python files in a directory.

    Args:
        directory (str): The directory to search in.
        exclude_dirs (List[str], optional): Directories to exclude. Defaults to ['venv'].
        exclude_files (List[str], optional): Files to exclude. Defaults to [].

    Returns:
        List[str]: List of file paths to Python files.
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
    Reads the entire content of a file.

    Args:
        path (str): The file path.

    Returns:
        str: The content of the file.
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
    Reads the content of all Python files in a directory,
    excluding specified files and directories.

    Args:
        directory (str): The root directory of the codebase.

    Returns:
        List[str]: A list of strings containing file paths and content.
    """
    exclude_files = ['craze.py', 'ibot.py', 'nextBuilderIntegration.py']
    exclude_dirs = ['interest', 'pyds', 'backup', 'models', 'sdlc',
                    'self_autoCode', 'self_autoCodebase', 'tests', 'to_confirm_tools']
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
