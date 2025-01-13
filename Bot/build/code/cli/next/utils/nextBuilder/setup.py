# utils\nextBuilder\setup.py
import shutil
import sys
import os


sys.path.append(os.getcwd())

# Importing the app_name variable from the shared module
from utils.shared import app_name  # nopep8


def copy_and_replace(source_path, destination_path):
    """
    Copies a file from source_path to destination_path.
    If the file at destination_path exists, it is removed before copying.
    """
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)  # Use rmtree for directories
    shutil.copytree(source_path, destination_path)


# Define the source and destination paths
migrations_src = 'utils/nextBuilder/base/migrations'
migrations_dest = os.path.join(app_name, 'src', 'migrations')

# Copy and replace the migrations directory
copy_and_replace(migrations_src, migrations_dest)

if app_name.endswith('macho'):
    other_sources_destinations = [
        ('utils/nextBuilder/base/data_macho', 'src/data'),
        ('utils/nextBuilder/base/public_macho', 'public'),
        ('utils/nextBuilder/base/.env.local', '.env.local'),
        ('utils/nextBuilder/base/app.js', 'app.js'),
    ]
else:
    other_sources_destinations = [
        ('utils/nextBuilder/base/data', 'src/data'),
        ('utils/nextBuilder/base/public', 'public'),
        ('utils/nextBuilder/base/.env.local', '.env.local'),
        ('utils/nextBuilder/base/app.js', 'app.js'),
    ]


for src, relative_dest in other_sources_destinations:
    dest = os.path.join(app_name, relative_dest)
    if os.path.isdir(src):
        copy_and_replace(src, dest)
    else:
        # For individual files, use a similar logic but with file operations
        if os.path.exists(dest):
            os.remove(dest)
        shutil.copy2(src, dest)

        
# print('Done Here')
