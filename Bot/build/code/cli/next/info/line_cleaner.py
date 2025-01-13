# building\info\line_cleaner.py
import os
import re

def process_file(file_path):
    """
    Process the specified file to ensure there are at most two consecutive empty lines.
    :param file_path: Path to the file to be processed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Use a regular expression to find three or more consecutive newline characters
        # and replace them with two newline characters
        modified_content = re.sub(r'\n{3,}', '\n\n', content)

        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_directory(directory):
    """
    Process all files in the specified directory, excluding __pycache__ directories.
    :param directory: Path to the directory to be processed.
    """
    for root, dirs, files in os.walk(directory):
        # Modify dirs in place to skip __pycache__ or any other directories you want to ignore
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            file_path = os.path.join(root, file)
            process_file(file_path)
            print(f"Processed {file_path}")

def main():
    directory = './building/'  # Replace with the path to your directory
    process_directory(directory)

if __name__ == '__main__':
    main()
