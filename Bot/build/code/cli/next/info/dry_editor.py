# Bot\build\code\cli\next\info\dry_editor.py
import shutil
import re
from typing import List

def create_working_copy(source_path: str, working_path: str) -> None:
    """
    Create a working copy of the given markdown file.
    
    Args:
        source_path (str): The path to the original markdown file.
        working_path (str): The path for the working copy.
    """
    shutil.copyfile(source_path, working_path)
    print(f"Working copy created: {working_path}")

def split_sections(text: str, separator_pattern: str = r'\n=+\n') -> List[str]:
    """
    Split the markdown text into sections using lines that consist only of '=' characters.
    
    Args:
        text (str): The entire markdown content.
        separator_pattern (str): The regex pattern used as a delimiter (default: lines of "=").
    
    Returns:
        List[str]: List of section strings.
    """
    sections = re.split(separator_pattern, text)
    return sections

def interactive_review(working_file: str, separator: str = "\n" + "="*30 + "\n") -> None:
    """
    Reads the working markdown file, splits it into sections,
    then for each section prints it and prompts the user.
    
    If the user confirms (by entering 'y') that the change has been implemented,
    the section is removed (i.e. not kept in the file). Otherwise, the section is kept.
    
    The updated markdown (only with the sections the user did not confirm) is written
    back to the working file.
    
    Args:
        working_file (str): Path to the working markdown file.
        separator (str): The separator string used between sections when writing the file.
    """
    with open(working_file, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = split_sections(content)
    remaining_sections = []

    for idx, section in enumerate(sections, start=1):
        print(f"\n--- Section {idx} ---")
        print(section)
        print("---------------------")
        answer = input(
            "Confirm that this change has been implemented? (y to delete, n to keep): ").strip().lower()
        if answer == 'y':
            print(f"Section {idx} will be removed.\n")
        else:
            print(f"Section {idx} will remain in the working document.\n")
            remaining_sections.append(section)

    new_content = separator.join(remaining_sections)
    with open(working_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Working file updated.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python review_md.py <source_md> <working_md>")
        sys.exit(1)

    source_md = sys.argv[1]
    working_md = sys.argv[2]

    # Create a working copy of the markdown file.
    create_working_copy(source_md, working_md)

    # Continue to review until no sections remain, or the user opts to exit.
    while True:
        interactive_review(working_md)
        with open(working_md, 'r', encoding='utf-8') as f:
            remaining = f.read().strip()
        if not remaining:
            print("All sections have been removed. Exiting.")
            break
        cont = input(
            "Do you want to review the remaining sections again? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting review loop.")
            break
