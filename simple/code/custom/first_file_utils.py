def create_file(file_path: str, content: str) -> str:
    """
    Creates a new file with the given content.

    Args:
        file_path: The path to the file to be created.
        content: The content to be written into the file.

    Returns:
        The full path to the written file.
    """
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"File created at: {file_path}"
    except Exception as e:
        return f"Error creating file: {e}"


def modify_file(file_path: str, content: str, line_number: int) -> str:
    """
    Modifies a specific line in a file with the given content.

    Args:
        file_path: The path to the file to be modified.
        content: The new content to be written into the specific line.
        line_number: The line number to be modified (1-indexed).

    Returns:
        The full path to the modified file.
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if line_number > len(lines):
            return f"Error: Line number {line_number} exceeds file length"
        
        lines[line_number - 1] = content + '\n'

        with open(file_path, 'w') as f:
            f.writelines(lines)
        return f"File modified at: {file_path}"
    
    except FileNotFoundError:
          return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error modifying file: {e}"
