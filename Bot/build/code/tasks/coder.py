# Bot\build\code\tasks\coder.py
import ast
import os
from typing import List

def find_functions_without_docstrings(path: str) -> List[ast.Dict]:
    """
    Recursively traverse the given directory or process a single file to find all functions and classes
    without docstrings.

    Args:
        path (str): The root directory or file to start searching from.

    Returns:
        List[Dict]: A list of dictionaries containing details about functions and classes without docstrings.
    """
    functions_without_docstrings = []

    if os.path.isfile(path):
        ### Process a single file        filepath = path
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                file_contents = f.read()
            tree = ast.parse(file_contents)
            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    docstring = ast.get_docstring(node)
                    if docstring is None:
                        functions_without_docstrings.append(
                            {
                                "file": filepath,
                                "line": node.lineno,
                                "name": node.name,
                                "type": (
                                    "Class"
                                    if isinstance(node, ast.ClassDef)
                                    else "Function"
                                ),
                            }
                        )
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Skipping file {filepath} due to parsing error: {e}")

    elif os.path.isdir(path):
        ### Recursively process a directory        
        for root, _, files in os.walk(path):
            ### Skip hidden directories like .git or __pycache__            
            if any(part.startswith(".") for part in root.split(os.sep)):
                continue
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            file_contents = f.read()
                        tree = ast.parse(file_contents)
                        for node in ast.walk(tree):
                            if isinstance(
                                node,
                                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
                            ):
                                docstring = ast.get_docstring(node)
                                if docstring is None:
                                    functions_without_docstrings.append(
                                        {
                                            "file": filepath,
                                            "line": node.lineno,
                                            "name": node.name,
                                            "type": (
                                                "Class"
                                                if isinstance(node, ast.ClassDef)
                                                else "Function"
                                            ),
                                        }
                                    )
                    except (SyntaxError, UnicodeDecodeError) as e:
                        print(
                            f"Skipping file {
                                filepath} due to parsing error: {e}"
                        )
    else:
        print(f"The path '{path}' is neither a valid file nor a directory.")

    return functions_without_docstrings

def improve_adherence_to_python_standards(code: str) -> str:
    ### Pseudo: run some style check or transformation logic    ### Or call black / autopep8 programmatically    
    return code
