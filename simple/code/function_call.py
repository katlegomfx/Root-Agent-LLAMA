# ./simple/code/function_call.py:
import tempfile
import subprocess
import os
import logging
import shlex
import traceback  # Import traceback
from typing import Any, Union, List

# from simple.code.logging_config import setup_logging # Assuming configured elsewhere
# setup_logging()

# Security Warning: Executing arbitrary bash commands is highly risky.
# Consider replacing this with specific Python functions or heavily sanitizing/validating input.


def execute_bash_command(command: str) -> str:
    """
    Executes a bash command provided as a string.

    Args:
        command: The command to execute.
                 - If string: Treated as a single command line, split by shlex.

    Returns:
        str: The standard output of the command if successful.

    Raises:
        ValueError: If the command format is unsupported or invalid.
        Exception: If the command fails to execute (non-zero exit code or other error).
                  The exception message includes stderr.
    """
    logging.warning(
        "Executing bash command. Ensure the command source is trusted and validated.")
    run_command_list: List[str] = []

    try:
        if isinstance(command, str):
            if not command.strip():
                raise ValueError("Command string cannot be empty.")
            run_command_list = shlex.split(command)
        elif isinstance(command, list):
            if not command:
                raise ValueError("Command list cannot be empty.")
            # Ensure all elements are strings
            if not all(isinstance(item, str) for item in command):
                raise ValueError(
                    "All elements in command list must be strings.")
            run_command_list = command
        elif isinstance(command, dict):
            cmd_str = command.get('command') or command.get('bash_command')
            if not cmd_str or not isinstance(cmd_str, str) or not cmd_str.strip():
                raise ValueError(
                    "Command dictionary must contain a non-empty string value for 'command' or 'bash_command' key.")
            run_command_list = shlex.split(cmd_str)
        else:
            raise ValueError(
                f"Unsupported command format: {type(command)}. Use str, list, or dict.")

        if not run_command_list:
            raise ValueError("Derived command list is empty after parsing.")

        logging.info(f"Executing bash command: {run_command_list}")
        # Use text=True for automatic decoding, explicitly set encoding
        completed = subprocess.run(
            run_command_list,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False  # Don't raise CalledProcessError automatically, check returncode manually
        )

        if completed.returncode != 0:
            stderr = completed.stderr.strip()
            error_message = (f"Command '{' '.join(run_command_list)}' failed with exit code {completed.returncode}"
                             f"{f', stderr: {stderr}' if stderr else ''}")
            logging.error(error_message)
            # Raise an exception that includes the error details
            raise Exception(error_message)
        else:
            stdout = completed.stdout.strip()
            logging.info(f"Bash command successful. Output: {stdout[:200]}...")
            return stdout

    except FileNotFoundError:
        # Error if the command itself (e.g., 'ls') isn't found
        error_message = f"Error executing bash command: Command '{run_command_list[0]}' not found."
        logging.error(error_message)
        raise Exception(error_message) from None  # Raise clean exception
    except ValueError as ve:  # Catch specific ValueErrors from validation
        logging.error(f"Invalid command input: {ve}")
        raise  # Re-raise the ValueError
    except Exception as e:
        # Catch other potential errors (like subprocess issues, permissions)
        # Avoid catching the Exception raised for non-zero return code if already logged
        if "failed with exit code" not in str(e):
            error_message = f"Error executing bash command '{run_command_list}': {e}\n{traceback.format_exc()}"
            logging.error(error_message)
            # Wrap unexpected errors in a standard Exception
            raise Exception(error_message) from e
        else:
            raise  # Re-raise the command failure exception


def write_custom_python_file(file_path: str, code: str) -> str:
    """
    Writes the provided Python code to a file within the 'simple/code/custom' directory.
    Prevents path traversal attacks.

    Args:
        file_path (str): The desired filename (e.g., "my_tool.py"). Should not contain path separators.
        code (str): The Python code content to write.

    Returns:
        str: The full path to the written file if successful.

    Raises:
        ValueError: If file_path is invalid or attempts path traversal.
        OSError: If file writing fails.
    """
    base_folder = os.path.abspath(os.path.join("simple", "code", "custom"))

    # Basic sanitization: remove leading/trailing whitespace and path separators
    # This is a simple check; more robust validation might be needed depending on usage.
    clean_filename = os.path.basename(file_path.strip())

    if not clean_filename or clean_filename != file_path.strip():
        raise ValueError(
            f"Invalid file_path '{file_path}'. It should be a simple filename without path separators.")

    # Ensure the filename ends with .py (optional, but good practice for Python tools)
    # if not clean_filename.lower().endswith('.py'):
    #     clean_filename += '.py' # Append if missing

    full_path = os.path.join(base_folder, clean_filename)

    # Final check: ensure the resolved path is still within the intended base folder
    if os.path.commonpath([base_folder, os.path.abspath(full_path)]) != base_folder:
        raise ValueError(
            f"Security risk: Invalid file path '{file_path}' attempts to write outside the allowed directory.")

    try:
        os.makedirs(base_folder, exist_ok=True)  # Ensure directory exists
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(code)
        logging.info(f"File successfully written to: {full_path}")
        print(f"File successfully written to: {full_path}")
        return full_path
    except OSError as e:
        logging.error(f"Failed to write file {full_path}: {e}")
        raise  # Re-raise OSError
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while writing file {full_path}: {e}\n{traceback.format_exc()}")
        raise OSError(
            f"Failed to write file {full_path} due to unexpected error.") from e


# Example usage within __main__ remains largely the same
if __name__ == "__main__":
    try:
        file_path = "example_tool.py"  # Simple filename
        code_content = (
            "import logging\n\n"
            "def sample_tool_function(params):\n"
            "    '''Example tool documentation.'''\n"
            "    logging.info(f'Sample tool executed with params: {params}')\n"
            "    return f'Processed: {params}'\n"
        )
        written_path = write_custom_python_file(file_path, code_content)

        # Example bash command (use with caution)
        # list_files_cmd = "ls -l simple/code/custom"
        # output = execute_bash_command(list_files_cmd)
        # print(f"\nBash command output for '{list_files_cmd}':\n{output}")

        # Example invalid path
        # write_custom_python_file("../outside_tool.py", "# Malicious code")

    except (ValueError, OSError, Exception) as e:
        print(f"\nAn error occurred: {e}")
