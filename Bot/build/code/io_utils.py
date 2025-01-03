import os
from Bot.build.code.session.constants import (
    code_prefix,
    assistant_prefix,
    summary_prefix,
    ai_code_path,
    ai_results_path,
    ai_history_path,
    ai_errors_path,
    ai_summaries_path,
    binary_answer,
    anonymised, error_file,
    triple_backticks,
    md_heading,
    gen_ai_path
)

def write_content_to_file(content: str, path: str) -> None:
    """Writes the given content to a file at the specified path."""
    with open(path, 'w') as f:
        f.write(content)


def get_next_filename_index(directory: str, prefix: str) -> int:
    """
    Returns the next available file index in the given directory for files 
    starting with the given prefix.
    """
    return len([item for item in os.listdir(os.path.join(gen_ai_path, directory)) if item.startswith(prefix)])
