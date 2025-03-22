import tempfile
import subprocess
import os
import logging
import shlex
from typing import Any


def execute_bash_command(command: Any) -> str:
    """
    Execute a bash command and return its output as a string.
    """
    try:
        if isinstance(command, dict):
            cmd_str = command.get('command') or command.get('bash_command')
            if not cmd_str:
                raise ValueError(
                    "Command dictionary is missing a required key.")
            run_command = shlex.split(cmd_str)
        elif isinstance(command, list):
            if len(command) == 1 and ' ' in command[0]:
                run_command = shlex.split(command[0])
            else:
                run_command = command
        elif isinstance(command, str):
            run_command = shlex.split(command)
        else:
            raise ValueError("Unsupported command format.")
        completed = subprocess.run(run_command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise Exception(
                f"Command failed with exit code {completed.returncode}, error: {completed.stderr}")
        return completed.stdout
    except Exception as e:
        logging.error(f"Error in bash command: {e}")
        return ""


def write_custom_python_file(file_path: str, code: str) -> None:
    """
    Writes the provided code to a Python file under the folder 'simple/code/custom'.
    """
    base_folder = os.path.join("simple", "code", "custom")
    os.makedirs(base_folder, exist_ok=True)
    full_path = os.path.join(base_folder, file_path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"File successfully written to: {full_path}")


if __name__ == "__main__":
    file_path = "example.py"  # File will be created as simple/code/custom/example.py
    code = (
        "def hello_world():\n"
        "    print('Hello, world!')\n\n"
        "if __name__ == '__main__':\n"
        "    hello_world()\n"
    )
    write_custom_python_file(file_path, code)
