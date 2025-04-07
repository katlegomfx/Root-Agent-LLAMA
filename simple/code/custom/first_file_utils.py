from typing import List
import os
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


def read_file(file_path: str) -> str:
    """
    Reads the content of a file and returns it as a string.

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        str: The content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If an error occurs while reading the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def delete_file(file_path: str) -> None:
    """
    Deletes a file from the file system.

    Args:
        file_path (str): The path to the file to be deleted.

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If the file cannot be deleted.
    """
    os.remove(file_path)


def rename_move_file(src: str, dst: str) -> None:
    """
    Renames or moves a file from a source path to a destination path.

    Args:
        src (str): The current file path.
        dst (str): The new file path or destination.

    Raises:
        FileNotFoundError: If the source file does not exist.
        OSError: If the file cannot be moved or renamed.
    """
    os.rename(src, dst)


def list_directory_contents(directory: str) -> List[str]:
    """
    Lists the contents of a directory.

    Args:
        directory (str): The directory to list the contents of.

    Returns:
        List[str]: A list containing the names of entries in the directory.

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the specified path is not a directory.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory} is not a valid directory.")
    return os.listdir(directory)
