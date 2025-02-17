# Bot\build\code\tasks\base_execute.py
import contextlib
import io
from typing import Dict, Any

from colorama import Fore
from Bot.build.code.cli.cli_helpers import colored_print, strip_model_escapes
from Bot.build.code.tasks.run_commands import (
    execute_bash_command,
    fetch_url_content,
    http_post_data
)

tool_registry = {
    execute_bash_command.__name__: execute_bash_command,
    fetch_url_content.__name__: fetch_url_content,
    http_post_data.__name__: http_post_data,
}

def execute_code(code: str) -> Dict[str, str]:
    """
    Executes a string of Python code using exec() and captures stdout.

    Returns:
        Dict[str, str]: A dictionary with "status" (200 or 500) and "message" (output or error).
    """
    output = io.StringIO()
    result = {"status": "", "message": ""}
    colored_print("Executing Python code...", color=Fore.BLUE)
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {})
        value = output.getvalue()
        colored_print(value, color=Fore.MAGENTA)
        result['status'] = "200"
        result['message'] = "Execution successful\nResult:\n" + value
    except Exception as e:
        result['status'] = "500"
        result['message'] = f"Execution failed:\n{str(e)}"
    return result

def execute_tool(instruction: Dict[str, Any]) -> Dict[str, str]:
    """
    Execute a named tool with the provided parameters.

    Example:
        instruction = {
            "tool": "execute_bash_command",
            "parameters": "ls -l"
        }

    Returns:
        Dict[str, str]: "status" (200 or 500) and "message" (output or error).
    """
    result = {"status": "", "message": ""}
    tool_name = instruction.get('tool')
    if not tool_name:
        colored_print("No tool specified in the instruction.", color=Fore.BLUE)
        result['status'] = "500"
        result['message'] = "Error: No tool specified."
        return result

    tool_func = tool_registry.get(tool_name)
    if not tool_func:
        colored_print(
            f"Tool {tool_name} not found in registry.", color=Fore.BLUE)
        result['status'] = "500"
        result['message'] = f"Error: Tool {tool_name} not found."
        return result

    params = instruction.get('parameters')
    try:
        colored_print(f"Executing tool: {tool_name} with parameters: {
                      params}", color=Fore.BLUE)
        output = tool_func(params)
        if output is None:
            raise Exception("Tool returned None (possibly an error).")
        section_clean = strip_model_escapes(output)
        colored_print(f"Tool execution results:\n{
                      section_clean}", color=Fore.MAGENTA)
        result['status'] = "200"
        result['message'] = f"Execution successful\nResult:\n{output}"
    except Exception as e:
        colored_print(f"Error executing tool {
                      tool_name}: {e}", color=Fore.BLUE)
        result['status'] = "500"
        result['message'] = f"Execution failed:\n{str(e)}"
    return result
