import os
from datetime import datetime
import subprocess
from typing import Any, List, Dict
import logging

logging.basicConfig(level=logging.INFO)

thesysname = "You are Flexi💻AI."
DEFAULT_PROMPT_FILE = "flexi.txt"
DEFAULT_PROMPT_CONTENT = f"{thesysname}. You think step by step, keeping key points in mind to solve or answer the request."
MD_HEADING = "#"
TRIPLE_BACKTICKS = "```"


def execute_bash_command(command: any) -> str:
    """
    Execute a bash command and return its output as a string.
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
            run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            raise Exception(
                f"Command failed with exit code {process.returncode}, error: {error.decode('utf-8')}")
        return output.decode('utf-8')
    except Exception as e:
        logging.error(f"Error in bash command: {e}")
        return ""


tool_registry = {
    execute_bash_command.__name__: execute_bash_command,
}


def add_context_to_messages(messages: List[Dict[str, str]], summary: str) -> List[Dict[str, str]]:
    """
    Appends a summary context to each system message if provided.
    """
    if summary:
        for msg in messages:
            if msg.get('role') == 'system':
                msg['content'] += f"\n\nSummary Context:\n{summary}"
    return messages


def load_message_template(sys_type: str = 'base', summary: str = '') -> List[Dict[str, str]]:
    sys_type = sys_type.lower()
    if sys_type == "base":
        content = f"""
{MD_HEADING} {thesysname}, an advanced AI agent capable of reflection and tool usage.
{MD_HEADING} You must handle user requests by reasoning step by step:
{MD_HEADING} 1) Understand the user request.
{MD_HEADING} 2) Choose if you will use a tool or python.
{MD_HEADING} Respond with your choice in a JSON object wrapped in triple backticks.
{MD_HEADING} Usage:
- Provide a **JSON** response wrapped in triple backticks and with JSON indicated (start with {TRIPLE_BACKTICKS}json)
- The response should contain the name of the executor to use (either "python" or "tool").
- Schema Example:
    {TRIPLE_BACKTICKS}json
    {{"use": "<name>"}}
    {TRIPLE_BACKTICKS}
- Example 1:
    {TRIPLE_BACKTICKS}json
    {{"use": "tool"}}
    {TRIPLE_BACKTICKS}
- Example 2:
    {TRIPLE_BACKTICKS}json
    {{"use": "python"}}
    {TRIPLE_BACKTICKS}
{MD_HEADING} Available Tools:
{MD_HEADING} Names:
[{", ".join(tool_registry.keys())}]
{MD_HEADING} Documentation:
[{", ".join([(tool_registry[tool].__doc__ or "").strip() for tool in tool_registry.keys()])}]
"""
        message = [{'role': 'system', 'content': content.strip()}]
    elif sys_type == "answer":
        content = f"""{MD_HEADING} {thesysname}, an advanced AI agent, answer as best you can."""
        message = [{'role': 'system', 'content': content.strip()}]

    elif sys_type == "check":
        content = f"""
{MD_HEADING} {thesysname}, an advanced AI agent capable of reflection and tool usage.
{MD_HEADING} You must handle user requests by reasoning step by step:
{MD_HEADING} 1) Understand the user request.
{MD_HEADING} 2) Decide if the user's request was achieved.
{MD_HEADING} Respond with your decision in a JSON object wrapped in triple backticks.
{MD_HEADING} Schema Example:
    {TRIPLE_BACKTICKS}json
    {{"use": "<yes or no>"}}
    {TRIPLE_BACKTICKS}
"""
        message = [{'role': 'system', 'content': content.strip()}]
    elif sys_type == "tool":
        content = f"""{MD_HEADING} {thesysname}, an advanced AI agent with tool usage capabilities.
{MD_HEADING} Steps:
1) Understand the user request.
2) If a tool is required, output a JSON instruction wrapped in triple backticks.
3) If the tool execution fails, reflect on the error and try again with corrected parameters.
4) Provide the final result or explanation.
{MD_HEADING} Available Tools:
Names: [{", ".join(tool_registry.keys())}]
Documentation: [{", ".join([(tool_registry[tool].__doc__ or "").strip() for tool in tool_registry.keys()])}]
{MD_HEADING} Usage:
- Output a JSON response wrapped in triple backticks.
- Include the tool name and parameters.
Example:
    {TRIPLE_BACKTICKS}json
    {{"tool": "<name>", "parameters": "<values>"}}
    {TRIPLE_BACKTICKS}
"""
        message = [{'role': 'system', 'content': content.strip()}]
    elif sys_type == "summary":
        message = [{'role': 'system', 'content': f"{MD_HEADING} You are a personal assistant. Extract and summarize key points from the provided text."}]
    elif sys_type not in ["tool", ]:
        message = [
            {'role': 'system',
                'content': f'{MD_HEADING} You are an expert {sys_type.capitalize()} Developer'}
        ]

    else:
        message = [
            {'role': 'system', 'content': f"{MD_HEADING} You are an expert {sys_type.capitalize()} Developer."}]
    return add_context_to_messages(message, summary)
