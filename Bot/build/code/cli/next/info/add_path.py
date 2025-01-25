# Bot\build\code\cli\next\info\add_path.py
import os
import logging

def prepend_file_location_check(directory, extensions, files_to_keep=None, ignored_directories=None, ignored_files=None):
    """
    Prepend each file in the directory with its location as a comment on the first line.
    Only for files with the given extensions. Check if the comment is already present.
    
    Parameters:
    - directory: The directory to process.
    - extensions: A tuple of file extensions to process.
    - files_to_keep (optional): A list of specific filenames to keep unmodified.
    - ignored_directories (optional): A list of directories to skip.
    - ignored_files (optional): A list of specific filenames to ignore.
    """
    if files_to_keep is None:
        files_to_keep = []

    if ignored_directories is None:
        ignored_directories = []

    if ignored_files is None:
        ignored_files = []

    for root, dirs, files in os.walk(directory):

        dirs[:] = [d for d in dirs if d not in ignored_directories]

        for file in files:
            if file not in files_to_keep and file not in ignored_files and file.endswith(extensions):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                comment_str = f"# {relative_path}"

                try:
                    with open(file_path, 'r+') as f:

                        first_line = f.readline()
                        modified_first_line = first_line.replace('\n', '')

                        # logging.info(("##",first_line.replace('\n', ''), "##"))

                        # If the first line is not the comment string, prepend it
                        if comment_str not in first_line and comment_str != modified_first_line:
                            content = f.read()
                            f.seek(0, 0)
                            f.write(comment_str + "\n" +
                                    modified_first_line + "\n" + content)

                        else:
                            pass

                except Exception as e:
                    logging.error(
                        f"Error processing file {file_path}. Error: {str(e)}")
                    
def run_it():
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Applying the function to the provided directory
    directory_to_process = "."
    extensions_to_process = ('.py')
    files_to_keep = [
        "next-env.d.js",
        "next.config.js",
        "package.json",
        "postcss.config.js",
        "tailwind.config.js",
        "jsconfig.json"
    ]
    ignored_directories = ["node_modules",
                           ".next", "jsBuild", "jsBuilds", "pyllms", "results"]

    prepend_file_location_check(
        directory_to_process, extensions_to_process, files_to_keep, ignored_directories)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Applying the function to the provided directory
    directory_to_process = "."
    extensions_to_process = ('.py')
    files_to_keep = [
        "next-env.d.js",
        "next.config.js",
        "package.json",
        "postcss.config.js",
        "tailwind.config.js",
        "jsconfig.json"
    ]
    ignored_directories = ["node_modules",
                           ".next", "jsBuild", "jsBuilds", "pyllms", "results"]

    prepend_file_location_check(
        directory_to_process, extensions_to_process, files_to_keep, ignored_directories)
