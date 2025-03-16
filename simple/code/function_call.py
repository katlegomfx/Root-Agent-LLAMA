import tempfile
import subprocess
import os
import logging

from simple.code.system_prompts import tool_registry

def execute_python_code(code: str) -> dict:
    """
    Executes a string of Python code in a separate process.
    Writes the code to a temporary file and runs it via the system Python interpreter.
    Returns:
        Dict[str, str]: A dictionary with "status" and "message".
    """
    result = {"status": "", "message": ""}
    temp_filename = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as temp_file:
            temp_file.write(code)
            temp_filename = temp_file.name
        process = subprocess.Popen(
            ["python", temp_filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            result['status'] = "500"
            result[
                'message'] = f"Execution failed with exit code {process.returncode}:\n{stderr.decode('utf-8')}"
        else:
            result['status'] = "200"
            result['message'] = "Execution successful\nResult:\n" + \
                stdout.decode('utf-8')
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
    tool_func = tool_registry.get(tool_name)
    if not tool_func:
        logging.error(f"Tool {tool_name} not found in registry.")
        result['status'] = "500"
        result['message'] = f"Error: Tool {tool_name} not found."
        return result
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
