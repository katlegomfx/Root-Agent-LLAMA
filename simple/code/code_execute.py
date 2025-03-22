import tempfile
import subprocess
import os
import sys
import logging

from simple.agent_interactions import move_to_tool_dynamic


def execute_python_code(code: str) -> dict:
    """
    Executes a string of Python code in a separate process.
    Writes the code to a temporary file and runs it via the system Python interpreter.

    Returns:
        dict: A dictionary with "status" and "message".
    """
    result = {"status": "", "message": ""}
    temp_filename = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as temp_file:
            temp_file.write(code)
            temp_filename = temp_file.name
        completed = subprocess.run(
            [sys.executable, temp_filename],
            capture_output=True,
            text=True
        )
        if completed.returncode != 0:
            result['status'] = "500"
            result['message'] = f"Execution failed with exit code {completed.returncode}:\n{completed.stderr}"
        else:
            result['status'] = "200"
            result['message'] = "Execution successful\nResult:\n" + \
                completed.stdout
    except Exception as e:
        result['status'] = "500"
        result['message'] = f"Execution failed:\n{str(e)}"
    finally:
        if temp_filename and os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception:
                pass
    return result


def execute_tool(instruction: dict) -> dict:
    """
    Execute a named tool with the provided parameters.
    """
    result = {"status": "", "message": ""}
    tool_name = instruction.get('tool')
    if not tool_name:
        logging.error("No tool specified in the instruction.")
        result['status'] = "500"
        result['message'] = "Error: No tool specified."
        return result

    from simple.code.tool_registry import tool_registry

    tool_func = tool_registry.get(tool_name)

    if not tool_func:
        logging.error(f"Tool {tool_name} not found in registry.")
        result['status'] = "500"
        result['message'] = f"Error: Tool {tool_name} not found."
        return result
    move_to_tool_dynamic(tool_name)
    params = instruction.get('parameters')
    try:
        logging.info(f"Executing tool: {tool_name} with parameters: {params}")
        output = tool_func(params)
        if output is None:
            raise Exception("Tool returned None (possibly an error).")
        result['status'] = "200"
        result['message'] = f"Execution successful\nResult:\n{output}"
    except Exception as e:
        logging.error(f"Error executing tool {tool_name}: {e}")
        result['status'] = "500"
        result['message'] = f"Execution failed:\n{str(e)}"
    return result
