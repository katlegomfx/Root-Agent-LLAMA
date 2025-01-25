# Bot\build\code\utils\text_crud.py
import os

def read_file_lines(file_path: str) -> list:
    """
    Reads the entire file and returns a list of lines.

    Args:
        file_path (str): The path to the file.

    Returns:
        list: A list of strings, one for each line in the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def write_file_lines(file_path: str, lines: list) -> None:
    """
    Writes the provided list of lines to the file.

    Args:
        file_path (str): The path to the file.
        lines (list): A list of lines (strings) to write.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def append_line(file_path: str, new_line: str) -> None:
    """
    Appends a new line to the end of the file.

    Args:
        file_path (str): The path to the file.
        new_line (str): The line to append.
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(new_line + '\n')

def update_line(file_path: str, line_number: int, new_line: str) -> None:
    """
    Updates a specific line in the file.

    Args:
        file_path (str): The file to update.
        line_number (int): The 1-indexed line number to update.
        new_line (str): The new text to replace that line.
    
    Raises:
        IndexError: If line_number is out of range.
    """
    lines = read_file_lines(file_path)
    index = line_number - 1  # convert to 0-indexed
    if index < 0 or index >= len(lines):
        raise IndexError("Line number out of range.")
    lines[index] = new_line + '\n'
    write_file_lines(file_path, lines)

def delete_line(file_path: str, line_number: int) -> None:
    """
    Deletes a specific line from the file.

    Args:
        file_path (str): The file from which to delete the line.
        line_number (int): The 1-indexed line number to delete.
    
    Raises:
        IndexError: If line_number is out of range.
    """
    lines = read_file_lines(file_path)
    index = line_number - 1
    if index < 0 or index >= len(lines):
        raise IndexError("Line number out of range.")
    del lines[index]
    write_file_lines(file_path, lines)

def insert_line(file_path: str, line_number: int, new_line: str) -> None:
    """
    Inserts a new line at the specified line number.

    Args:
        file_path (str): The file to update.
        line_number (int): The 1-indexed position where the new line should be inserted.
                            If greater than number of lines, the line is appended.
        new_line (str): The line to insert.
    """
    lines = read_file_lines(file_path)
    index = line_number - 1
    if index < 0:
        index = 0
    elif index > len(lines):
        index = len(lines)
    lines.insert(index, new_line + '\n')
    write_file_lines(file_path, lines)

# Example usage:
if __name__ == "__main__":
    test_file = "test.txt"

    # Create a sample file if it doesn't exist.
    if not os.path.exists(test_file):
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Line 1\nLine 2\nLine 3\n")

    print("Original file lines:")
    for idx, line in enumerate(read_file_lines(test_file), start=1):
        print(f"{idx}: {line}", end="")

    # Append a new line
    append_line(test_file, "Line 4")

    # Update line 2
    update_line(test_file, 2, "Updated Line 2")

    # Delete line 1
    delete_line(test_file, 1)

    # Insert a new line at position 2
    insert_line(test_file, 2, "Inserted at line 2")

    print("\nUpdated file lines:")
    for idx, line in enumerate(read_file_lines(test_file), start=1):
        print(f"{idx}: {line}", end="")
