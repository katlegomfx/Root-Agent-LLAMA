### building\code\general\tools.pyimport os
import shutil

def ensure_folder_exists(folder):
    os.makedirs(folder, exist_ok=True)

def create_llm_result(folder, data):
    ensure_folder_exists(folder)
    num = len(os.listdir(folder))
    filenaming = f'query{num}.md'
    with open(os.path.join(folder, filenaming), 'w', encoding='utf-8') as f:
        final_str = f"{data}"
        f.write(final_str)

def empty_directory(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)  # Remove files and links
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Remove directories

def write_to_file(file_path, content):
    """Write given content to a specified file path."""
    try:
        ensure_folder_exists(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return (
            True, f"File '{file_path}' created successfully")
    except Exception as e:
        return (
            False, f"Failed to create file '{file_path}'. Reason: {e}")
