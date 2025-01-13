### building\run_command.pyimport shlex
import os
import subprocess

### List of allowed commandsALLOWED_COMMANDS = {'ls', 'echo', 'grep', 'py', 'npm', 'python', 'node', 'date'}
BASE_DIR = os.path.abspath("./projects")

def run_command(command_line):
    """
    Executes a specified system command within the BASE_DIR directory. ALLOWED_COMMANDS = {{'ls', 'echo', 'grep', 'py', 'npm', 'python', 'node', 'date'}}
    Expected Arguments: command_line='ls -la'
    """
    try:
        ### Split the command line into parts        command_parts = shlex.split(command_line)

        ### Extract the base command        base_command = command_parts[0]

        if base_command not in ALLOWED_COMMANDS:
            raise ValueError(f"Command '{base_command}' is not permitted.")

        ### Prepare the command for execution, ensuring each part is safely quoted        safe_command = [shlex.quote(part) for part in command_parts]

        ### Execute the command in the specified base directory        result = subprocess.run(
            safe_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=BASE_DIR,  # Set the current working directory to BASE_DIR
            shell=True,  # Important: Allows the command to be executed through the shell
            timeout=10)  # Set a timeout for the command execution

        stdout = result.stdout.decode()
        stderr = result.stderr.decode()

        if stderr:
            print(f"Error in command execution: {stderr}")

        data = {}
        if stderr:
            data['error'] = stderr
        if stdout:
            data['out'] = stdout

        return (
            True, "Command executed successfully", data)
    except Exception as e:
        return (
            False, f"An error occurred during command execution: {e}")

