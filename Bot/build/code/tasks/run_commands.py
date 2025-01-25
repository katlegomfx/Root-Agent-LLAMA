# Bot\build\code\tasks\run_commands.py
import subprocess
import requests

import subprocess

def execute_bash_command(command: str) -> str:
    """
    Execute a bash command and return its output.

    Args:
        command (str): The bash command to be executed.

    Returns:
        str: The output of the executed bash command.
    """
    try:
        if isinstance(command, dict):
            ### Check if 'command' key exists in the dictionary            
            if 'command' in command:
                ### Execute the command with its value                
                run_command = command['command'].split()

            elif 'bash_command' in command:
                ### Use the bash_command directly                
                run_command = command['bash_command'].split()
            else:
                raise ValueError("Command dictionary is missing required key")
            
        elif isinstance(command, list):
            ### If it's a list, use it as-is            
            run_command = command
        if isinstance(command, str):
            ### If it's a string, split it into separate commands            
            run_command = command.split()

        process = subprocess.Popen(run_command, stdout=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode != 0:
            raise Exception(f"Command failed with exit code {
                            process.returncode}")

        return output.decode('utf-8')
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"An error occurred while executing the bash command: {e}")
        return None

def fetch_url_content(url: str) -> str:
    """
    Fetch the content of a specified URL.

    Args:
        url (str): The URL to be fetched.

    Returns:
        str: The content of the specified URL.
    """

    try:
        response = requests.get(url, timeout=5)
        return response.text
    except requests.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")
        return None

def http_post_data(data: dict) -> str:
    """
    Send a POST request to the specified URL with optional data.
    
    Args:
        data (dict): A dictionary containing at least:
            "url": str   -> The URL to post to
            "payload": dict -> The JSON or form payload
            "headers": dict -> (optional) Additional headers

    Returns:
        str: The response text or error message
    """
    try:
        url = data.get('url')
        if not url:
            return "Error: Missing 'url' in parameters."

        ### You can decide how to handle payload vs. headers        
        payload = data.get('payload', {})
        headers = data.get('headers', {})

        ### Example: sending JSON        
        response = requests.post(
            url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"An error occurred while sending POST request: {e}"
