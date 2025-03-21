import tempfile
import subprocess
import os
import logging
import shlex


def execute_bash_command(command: any) -> str:
    """
    Execute a bash command and return its output as a string.
    """
    try:
        if isinstance(command, dict):
            if 'command' in command:
                run_command = shlex.split(command['command'])
            elif 'bash_command' in command:
                run_command = shlex.split(command['bash_command'])
            else:
                raise ValueError(
                    "Command dictionary is missing a required key.")
        elif isinstance(command, list):
            if len(command) == 1 and ' ' in command[0]:
                run_command = shlex.split(command[0])
            else:
                run_command = command
        elif isinstance(command, str):
            run_command = shlex.split(command)
        else:
            raise ValueError("Unsupported command format.")
        process = subprocess.Popen(
            run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            raise Exception(
                f"Command failed with exit code {process.returncode}, error: {error.decode('utf-8')}")
        return output.decode('utf-8')
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
    # Example usage:
    file_path = "example.py"  # File will be created as simple/code/custom/example.py
    code = (
        "def hello_world():\n"
        "    print('Hello, world!')\n\n"
        "if __name__ == '__main__':\n"
        "    hello_world()\n"
    )
    write_custom_python_file(file_path, code)
