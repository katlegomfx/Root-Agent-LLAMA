
import shutil
import os

def copy_py_files(src_dir, dst_dir):
    """
    Recursively copies all files from src_dir to dst_dir.
    
    Args:
        src_dir (str): The source directory containing files to be copied.
        dst_dir (str): The destination directory where the files will be copied.
    """

    # Check if the source and destination directories exist
    if not os.path.exists(src_dir):
        print(f"Source directory '{src_dir}' does not exist.")
        return


    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                src_file = os.path.join(root, file)
                print(src_file)

                dst_file = os.path.join(
                    dst_dir, os.path.relpath(src_file, src_dir))
                print(dst_file)

                new_path = '\\'.join(src_file.split('\\')[:-1])
                create_path = ''.join(new_path.split('/')[-1])

                full_create_path = os.path.join(dst_dir, create_path)
        
                print(full_create_path)
                os.makedirs(full_create_path, exist_ok=True)
        


        
                # Copy the file
                try:
                    shutil.copy2(src_file, dst_file)
                    print(f"Copied '{src_file}' to '{dst_file}'")
                except Exception as e:
                    print(f"Failed to copy '{src_file}': {e}")

# Example usage:
if __name__ == "__main__":
    src_dir = '../finalFirst/'
    dst_dir = './idea/AINextJS/'

    copy_py_files(src_dir, dst_dir)
