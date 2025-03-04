import os
import re




def get_py_files_recursive(directory, exclude_dirs=None, exclude_files=None):
    """
    Recursively searches for Python files in a directory.
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
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Adjust header markers for consistency
        return content.replace('##### ', '###### ')
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return ""


def code_corpus(path: str) -> list:
    """
    Reads the content of all Python files in a directory.
    """
    exclude_files = ['craze.py', 'ibot.py', 'nextBuilderIntegration.py']
    exclude_dirs = ['interest', 'pyds', 'backup', 'models', 'sdlc',
                    'self_autoCode', 'self_autoCodebase', 'tests', 'to_confirm_tools']
    paths = get_py_files_recursive(
        path, exclude_dirs=exclude_dirs, exclude_files=exclude_files)
    corpus = []
    for file_path in paths:
        try:
            text = read_file_content(file_path)
            corpus.append(f'\n###### {file_path}:\n{text}\n')
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    return corpus
