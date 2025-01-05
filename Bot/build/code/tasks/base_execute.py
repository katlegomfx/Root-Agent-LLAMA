from typing import Dict, Any
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


def execute_tool(instruction: Dict[str, Any]) -> str:
    """
    Execute a named tool with the provided parameters.

    Example instruction dict:
    {
        "tool": "execute_bash_command",
        "parameters": "ls -l"
    }
    """
    tool_name = instruction.get('tool')
    if not tool_name:
        print("No tool specified in the instruction.")
        return "Error: No tool specified."

    tool_func = tool_registry.get(tool_name)
    if not tool_func:
        print(f"Tool {tool_name} not found in registry.")
        return f"Error: Tool {tool_name} not found."

    params = instruction.get('parameters')
    try:
        print(f"Executing tool: {tool_name} with parameters: {params}")
        result = tool_func(params)
        print(f"Execution results: {result}")
        return result
    except Exception as e:
        print(f"Error executing tool {tool_name}: {e}")
        return f"Error: {e}"
