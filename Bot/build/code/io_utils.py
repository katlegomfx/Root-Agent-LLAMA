# Bot\build\code\io_utils.py
import os
import json
from Bot.build.code.session.constants import (
    gen_ai_path
)

def write_content_to_file(content: str, path: str) -> None:
    """Writes the given content to a file at the specified path."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_next_filename_index(directory: str, prefix: str) -> int:
    """
    Returns the next available file index in the given directory for files 
    starting with the given prefix.
    """
    return len([item for item in os.listdir(os.path.join(gen_ai_path, directory)) if item.startswith(prefix)])

def load_history(self):
    if not os.path.exists("file_path"):
        return []
    with open("file_path", 'r') as file:
        return json.load(file)
    

def store_history(self):
    with open("file_path", 'w') as file:
        json.dump(self, file, indent=4)

