import tempfile
import subprocess
import os
import sys
import logging
import traceback  # Keep this import


EXECUTION_TIMEOUT_SECONDS = 60  # Define timeout constant


def execute_python_code(code: str) -> dict:
    """
    Executes a string of Python code in a separate process using a temporary file.

    Args:
        code (str): The Python code to execute.

    Returns:
        dict: A dictionary containing:
              - "status" (str): "200" for success, "500" for error, "TIMEOUT" for timeout.
              - "message" (str): Execution result (stdout) or error details (stderr, traceback).
    """
    result = {"status": "500",
        "message": "Execution did not complete."}  # Default to error
    temp_filename = None

    if not code or not code.strip():
        result['message'] = "Execution failed: No code provided."
        logging.warning("execute_python_code called with empty code string.")
        return result

    try:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding='utf-8') as temp_file:
            temp_file.write(code)
            temp_filename = temp_file.name
        logging.info(f"Executing code in temporary file: {temp_filename}")

        completed = subprocess.run(
            [sys.executable, temp_filename],
            capture_output=True,
            text=True,  # Decodes stdout/stderr as text
            encoding='utf-8',  # Explicitly set encoding
            timeout=EXECUTION_TIMEOUT_SECONDS  # Use the defined timeout
        )

        if completed.returncode == 0:
            result['status'] = "200"
            stdout = completed.stdout.strip()
            result['message'] = f"Execution successful.\nOutput:\n{stdout}" if stdout else "Execution successful.\nOutput:\n[No output]"
            logging.info(
                f"Code execution successful. Output: {stdout[:200]}...")
        else:
            result['status'] = "500"
            stderr = completed.stderr.strip()
            result['message'] = f"Execution failed with exit code {completed.returncode}.\nError:\n{stderr}"
            logging.error(
                f"Code execution failed (Exit Code {completed.returncode}). Error: {stderr}")

    except subprocess.TimeoutExpired:
        result['status'] = "TIMEOUT"
        result['message'] = f"Execution timed out after {EXECUTION_TIMEOUT_SECONDS} seconds."
        logging.error(result['message'])
    except FileNotFoundError:
        result['status'] = "500"
        result['message'] = f"Execution failed: Python interpreter not found at '{sys.executable}'."
        logging.critical(result['message'])
    except Exception as e:
        result['status'] = "500"
        result['message'] = f"Execution failed due to an unexpected error: {str(e)}\n{traceback.format_exc()}"
        logging.error(result['message'])
    finally:
        if temp_filename and os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
                logging.info(f"Removed temporary file: {temp_filename}")
            except OSError as e:
                logging.error(
                    f"Error removing temporary file {temp_filename}: {e}")
            except Exception as e:  # Catch any other potential permission issues etc.
                logging.error(
                    f"Unexpected error removing temporary file {temp_filename}: {e}")

    return result


def execute_tool(instruction: dict, agent_manager) -> dict:
    """
    Executes a registered tool function based on the instruction dictionary.

    Args:
        instruction (dict): Expected to have 'tool' (str) and 'parameters' (any, passed to tool).
        agent_manager (AgentInteractionManager): Instance to control the visual agent.

    Returns:
        dict: A dictionary containing:
              - "status" (str): "200" for success, "500" for error.
              - "message" (str): Tool output or error details.
    """
    result = {"status": "500", "message": "Tool execution did not complete."}

    if not isinstance(instruction, dict):
        result['message'] = "Error: Instruction must be a dictionary."
        logging.error(result['message'])
        return result

    tool_name = instruction.get('tool')
    if not tool_name or not isinstance(tool_name, str):
        result['message'] = "Error: 'tool' key (string) missing or invalid in instruction."
        logging.error(f"{result['message']} Instruction: {instruction}")
        return result

    from simple.code.tool_registry import tool_registry

    tool_func = tool_registry.get(tool_name)
    if not tool_func or not callable(tool_func):
        result['message'] = f"Error: Tool '{tool_name}' not found or is not callable."
        logging.error(
            f"{result['message']} Available tools: {list(tool_registry.keys())}")
        return result

    agent_manager.move_to_tool_dynamic(tool_name)

    params = instruction.get('parameters')
    logging.info(f"Executing tool '{tool_name}' with parameters: {params}")

    try:
        if params is not None:
            output = tool_func(**params)
        else:
            try:
                 output = tool_func()  # Try calling without args if None provided
            except TypeError:
                logging.warning(f"Tool '{tool_name}' called without parameters, but might require them.")
                output = tool_func(params)  # Retry with None, maybe it handles it internally

        output_str = str(output)  # Convert result to string for the message
        result['status'] = "200"
        result['message'] = f"Tool '{tool_name}' executed successfully.\nResult:\n{output_str}"
        logging.info(
            f"Tool '{tool_name}' successful. Result: {output_str[:200]}...")

    except Exception as e:
        error_details = f"Error executing tool '{tool_name}': {str(e)}\n{traceback.format_exc()}"
        result['status'] = "500"
        result['message'] = f"Tool execution failed:\n{error_details}"
        logging.error(error_details)

    return result
