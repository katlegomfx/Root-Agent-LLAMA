# building\info\code_cleaner.py
import os

def remove_second_comment_line(file_path):
    """
    Remove the second comment line from the file.
    
    Parameters:
    - file_path: The path to the file to be processed.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        if len(lines) >= 2 and (lines[0].startswith('// ') or lines[0].startswith('# ')) and \
           (lines[1].startswith('// ') or lines[1].startswith('# ')):
            # Remove the second comment line
            del lines[1]

            with open(file_path, 'w') as file:
                file.writelines(lines)
    except Exception as e:
        print(f"Error2 processing file {file_path}. Error: {str(e)}")

def list_files_with_comment_header(directory, extensions, ignored_directories=None):
    """
    List all files in the directory with given extensions where the first two lines start with '// ' or '# '.

    Parameters:
    - directory: The directory to process.
    - extensions: A tuple of file extensions to process.
    - ignored_directories (optional): A list of directories to skip.

    Returns:
    - A list of files meeting the criteria.
    """
    matching_files = []
    if ignored_directories is None:
        ignored_directories = []

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignored_directories]

        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        lines = [next(f) for _ in range(2)]
                        if all(line.startswith('// ') for line in lines) or all(line.startswith('# ') for line in lines):
                            matching_files.append(file_path)
                            # Call the function to remove the second comment line
                            remove_second_comment_line(file_path)
                except Exception as e:
                    print(
                        f"Error1 processing file {file_path}. Error: {str(e)}")
    return matching_files

if __name__ == "__main__":
    # Define your directory and file extensions
    directory_to_process = "."
    extensions_to_process = ('.py',)
    ignored_directories = ["node_modules",
                           ".next", "jsBuild", "jsBuilds", "results"]

    # Get the list of matching files
    files_with_headers = list_files_with_comment_header(
        directory_to_process, extensions_to_process, ignored_directories)

    # Print or process the list of matching files
    for file in files_with_headers:
        print(file)
