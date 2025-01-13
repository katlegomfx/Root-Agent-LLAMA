# utils\nextBuilder\database\database_rollback.py
import subprocess
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    app_name, npx_path
)

def execute_commands():
    commands = [
        f'{npx_path} sequelize db:seed:undo:all',
        f'{npx_path} sequelize db:migrate:undo:all',
    ]
    
    for command in commands:
        command = f'cd {app_name}/src && {command}'
        print(f"Executing: {command}")
        process = subprocess.Popen(command, shell=True)
        process.wait()  # Wait for the command to complete
        # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # stdout, stderr = process.communicate()
        # # print(stdout.decode('utf-8'))
        # if stderr:
        #     print(f"Error: {stderr.decode('utf-8')}")

if __name__ == "__main__":
    execute_commands()