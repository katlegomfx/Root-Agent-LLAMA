### building\file_system.pyimport os
import shutil

ignore_these = [
    '.next',
    'node_modules',
    'bootstrap',
    'vendor',
    'storage',
    'tests',
    'resources',
    'public',
    'lang',
    'factories',
    '.venv',
    'venv']

BASE_DIR = os.path.abspath("./projects")

def is_safe_path(path):
    """
    Check if the given path is a safe subpath within the base directory.
    :param path: The path to validate.
    """

    ### Check if the absolute path starts with the base directory    return ".." not in path

def get_directory_tree(start_path):
    """
    Retrieve a tree of files with specified extensions from a given directory.
    Expected Arguments: {'start_path': './'}
    """
    if not is_safe_path(start_path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    start_path = os.path.join(BASE_DIR, start_path)
    tree = []
    try:
        for root, dirs, files in os.walk(start_path):
            dirs[:] = [d for d in dirs if d not in ignore_these]
            for file in files:
                if file.endswith(('.py', '.tsx', '.js')):
                    ### Append relative path from BASE_DIR                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, BASE_DIR)
                    display_path = os.path.join(
                        './', rel_path).replace('\\', '/')
                    tree.append(display_path)
        return (
            True, "Directory tree retrieved successfully", {
                "directory": tree})
    except Exception as e:
        return (
            False, f"Failed to retrieve directory tree. Reason: {e}")

def check_existence(path):
    """
    Check if a specified path exists in the file system.
    Expected Arguments: {'path': './path/'}
    """
    if not is_safe_path(path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    path = os.path.join(BASE_DIR, path)
    if os.path.exists(path):
        return (True, f"'{path}' exists")
    else:
        return (False, f"'{path}' does not exist")

def create_directory(path):
    """
    Create a new directory at the specified path.
    Expected Arguments: {'path': './path/'}
    """
    if not is_safe_path(path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    path = os.path.join(BASE_DIR, path)
    try:
        os.makedirs(path, exist_ok=True)
        return (
            True, f"Directory '{path}' created successfully")
    except Exception as e:
        return (
            False, f"Failed to create directory '{path}'. Reason: {e}")

def edit_directory(old_path, new_path):
    """
    Rename or move a directory from one path to another.
    Expected Arguments: {'old_path': './current/path', 'new_path': './new/path'}
    """
    if not is_safe_path(new_path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    old_path = os.path.join(BASE_DIR, old_path)
    new_path = os.path.join(BASE_DIR, new_path)
    try:
        os.rename(old_path, new_path)
        return (
            True, f"Directory '{old_path}' moved/renamed successfully to '{new_path}'")
    except Exception as e:
        return (
            False,
            f"Failed to move/rename directory '{old_path}' to '{new_path}'. Reason: {e}")

def delete_directory(path):
    """
    Delete a directory at a specified path.
    Expected Arguments: {'path': './path/'}
    """
    if not is_safe_path(path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    path = os.path.join(BASE_DIR, path)
    try:
        shutil.rmtree(path)
        return (
            True, f"Directory '{path}' deleted successfully")
    except Exception as e:
        return (
            False, f"Failed to delete directory '{path}'. Reason: {e}")

def copy_directory(source_path, destination_path):
    """
    Copy a directory from a source path to a destination path.
    Expected Arguments: {'source_path': './source/directory/path', 'destination_path': './destination/directory/path'}
    """
    if not is_safe_path(destination_path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    source_path = os.path.join(BASE_DIR, source_path)
    destination_path = os.path.join(BASE_DIR, destination_path)
    try:
        shutil.copytree(source_path, destination_path)
        return (
            True, f"Directory '{source_path}' copied successfully to '{destination_path}'")
    except Exception as e:
        return (
            False, f"Failed to copy directory '{source_path}'. Reason: {e}")

def create_file(file_path, content):
    """
    Create a new file at a specified path with given content.
    Expected Arguments: {'file_path': './path/', 'content': 'file content'}
    """
    if not is_safe_path(file_path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    file_path = os.path.join(BASE_DIR, file_path)
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return (
            True, f"File '{file_path}' created successfully")
    except Exception as e:
        return (
            False, f"Failed to create file '{file_path}'. Reason: {e}")

def edit_specific_lines(file_path, line_numbers, new_content):
    """
    Edit specific lines in a file based on JSON payload.
    Expected Arguments: {'file_path': 'path/to/file', 'line_numbers': [list of line numbers], 'new_content': [list of new content]}
    """
    ### Basic validation    if not file_path or line_numbers is None or new_content is None:
        return (
            False,
            "Invalid request. Please provide file_path, line_numbers, and new_content.")

    ### Check if the lengths of line_numbers and new_content are the same    if len(line_numbers) != len(new_content):
        return (
            False, "The length of line_numbers and new_content must be the same.")

    ### Rest of the function remains the same...    ### Read the file and store the lines in a list    with open(file_path, 'r') as file:
        lines = file.readlines()

    ### Edit specific lines    for line_number, content in zip(line_numbers, new_content):
        if line_number < len(lines):
            lines[line_number] = content + '\n'
        else:
            return (
                False, f"Line number {line_number} is out of range for the file.")

    ### Write the updated content back to the file    with open(file_path, 'w') as file:
        file.writelines(lines)

    return (True, "File edited successfully")

def edit_file(file_path, content):
    """
    Edit the content of a file at a specified path.
    Expected Arguments: {'file_path': './path/', 'content': 'new file content'}
    """
    if not is_safe_path(file_path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    file_path = os.path.join(BASE_DIR, file_path)
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return (
            True, f"File '{file_path}' edited successfully")
    except Exception as e:
        return (
            False, f"Failed to edit file '{file_path}'. Reason: {e}")

def delete_file(file_path):
    """
    Delete a file at a specified path.
    Expected Arguments: {'file_path': './path/'}
    """
    if not is_safe_path(file_path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    file_path = os.path.join(BASE_DIR, file_path)
    try:
        os.remove(file_path)
        return (True, f"File '{file_path}' deleted successfully")
    except Exception as e:
        return (
            False, f"Failed to delete file '{file_path}'. Reason: {e}")

def copy_file(source_path, destination_path):
    """
    Copy a file from a source path to a destination path.
    Expected Arguments: {'source_path': './source/file/path', 'destination_path': './destination/file/path'}
    """
    if not is_safe_path(destination_path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    source_path = os.path.join(BASE_DIR, source_path)
    destination_path = os.path.join(BASE_DIR, destination_path)
    try:
        shutil.copy2(source_path, destination_path)
        return (
            True, f"File '{source_path}' copied successfully to '{destination_path}'")
    except Exception as e:
        return (
            False, f"Failed to copy file '{source_path}'. Reason: {e}")

def move_file(source_path, destination_path):
    """
    Move a file from a source path to a destination path.
    Expected Arguments: {'source_path': './source/file/path', 'destination_path': './destination/file/path'}
    """
    if not is_safe_path(destination_path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    source_path = os.path.join(BASE_DIR, source_path)
    destination_path = os.path.join(BASE_DIR, destination_path)
    try:
        shutil.move(source_path, destination_path)
        return (
            True, f"File '{source_path}' moved successfully to '{destination_path}'")
    except Exception as e:
        return (
            False, f"Failed to move file '{source_path}'. Reason: {e}")

def get_file_text(file_path):
    """
    Read and return the content of a file at a specified path.
    Expected Arguments: {'file_path': './path/'}
    """
    if not is_safe_path(file_path):
        return (
            False, "Invalid path. Directory traversal is not allowed.")

    path = os.path.join(BASE_DIR, file_path)
    try:
        with open(path, 'r') as file:
            content = file.read()
        return (
            True, "File content retrieved successfully", {
                "file": content})
    except Exception as e:
        return (
            False, f"Failed to read file '{path}'. Reason: {e}")

def replace_text_in_file(file_path, old_text, new_text):
    """
    Replace specified text with new text in a file based on JSON payload.
    Expected Arguments: {'file_path': 'path/to/file', 'old_text': 'text to replace', 'new_text': 'replacement text'}
    """
    ### Basic validation    if not file_path or old_text is None or new_text is None:
        return (
            False, "Invalid request. Please provide file_path, old_text, and new_text.")

    try:
        ### Read the file and replace the text        with open(file_path, 'r') as file:
            content = file.read()

        content = content.replace(old_text, new_text)

        ### Write the updated content back to the file        with open(file_path, 'w') as file:
            file.write(content)

        return (
            True, "Text replaced successfully in the file.")
    except Exception as e:
        return (False, f"Failed to replace text. Reason: {e}")
