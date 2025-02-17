# Bot\build\code\tasks\run_commands.py
import subprocess
from typing import Any
from colorama import Fore
import requests

from Bot.build.code.cli.cli_helpers import colored_print

def execute_bash_command(command: Any) -> str:
    """
    Execute a bash command and return its output as a string.

    Args:
        command (Any): Could be:
           - a dict with "command" or "bash_command" key
           - a list of strings (e.g. ["ls", "-l"] or ["ls -l"])
           - a single string (e.g. "ls -l")

    Returns:
        str or None: The stdout of the executed bash command, or None on error.
    """
    try:
        if isinstance(command, dict):
            if 'command' in command:
                run_command = command['command'].split()
            elif 'bash_command' in command:
                run_command = command['bash_command'].split()
            else:
                raise ValueError(
                    "Command dictionary is missing a required key.")

        elif isinstance(command, list):
            if len(command) == 1 and ' ' in command[0]:
                run_command = command[0].split()
            else:
                run_command = command

        elif isinstance(command, str):
            run_command = command.split()
        else:
            raise ValueError("Unsupported command format.")

        process = subprocess.Popen(
            run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = process.communicate()

        if process.returncode != 0:
            raise Exception(
                f"Command failed with exit code {process.returncode}, "
                f"error: {error.decode('utf-8')}"
            )

        return output.decode('utf-8')

    except (ValueError, Exception) as e:
        colored_print(f"Error in bash command: {e}", color=Fore.RED)
        return None

def fetch_url_content(url: str) -> str:
    """
    Fetch the content of a specified URL.

    Returns:
        str or None: The content of the specified URL, or None on error.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        colored_print(f"Error fetching URL: {e}", color=Fore.RED)
        return None

def http_post_data(data: dict) -> str:
    """
    Sends a POST request to the specified URL with optional data.

    The data dictionary should have:
      - "url": str (required)
      - "payload": dict (optional, defaults to {})
      - "headers": dict (optional, defaults to {})

    Returns:
        str: The response text or an error message.
    """
    try:
        url = data.get('url')
        if not url:
            return "Error: Missing 'url' in parameters."

        payload = data.get('payload', {})
        headers = data.get('headers', {})

        response = requests.post(
            url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"An error occurred while sending POST request: {e}"
