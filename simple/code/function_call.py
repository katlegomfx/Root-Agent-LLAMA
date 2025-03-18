import tempfile
import subprocess
import os
import logging

# Removed: from simple.code.tool_registry import tool_registry


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

    # Import tool_registry locally to avoid circular dependency
    from simple.code.tool_registry import tool_registry

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


def write_custom_python_file(file_path: str, code: str) -> None:
    """
    Writes the provided code to a Python file under the folder 'simple/code/custom'.
    """
    base_folder = os.path.join("simple", "code", "custom")
    os.makedirs(base_folder, exist_ok=True)
    full_path = os.path.join(base_folder, file_path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"File successfully written to: {full_path}")


if __name__ == "__main__":
    # Example usage:
    file_path = "example.py"  # File will be created as simple/code/custom/example.py
    code = (
        "def hello_world():\n"
        "    print('Hello, world!')\n\n"
        "if __name__ == '__main__':\n"
        "    hello_world()\n"
    )
    write_custom_python_file(file_path, code)
