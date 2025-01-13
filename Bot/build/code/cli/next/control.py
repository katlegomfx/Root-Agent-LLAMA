### control.pyimport os
import os
import subprocess
import sys
from mysql.connector import Error
import mysql.connector
from contextlib import contextmanager

from Bot.build.code.cli.next.utils.shared import app_name, venv_name, node_path, npm_path, npx_path, ensure_folder_exists

def is_package_installed(package_name):
    """Check if a given Python package is installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def is_package_installed_in_next_app(application_name, package_name):
    """Check if a given npm package is installed in the application."""
    command = f"cd {application_name} && {npm_path} list {package_name}"
    with execute_command(command) as (stdout, stderr):
        if stdout:
            output = stdout.decode()
            print(output)
            return package_name in output
        if stderr:
            error_output = stderr.decode()
            print(error_output)
    return False

def check_venv_active():
    """Check if the correct virtual environment is active."""
    return venv_name in sys.executable

def check_db_service(db_name="flex_development"):
    """Check if a service is running on the specified port."""
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database=f"{db_name}"
        )
        if connection.is_connected():
            print("MySQL is running")
            return True
    except Error as e:
        print(f"Error: {e}")

def read_and_update_run_counter(counter_file_path):
    """Read and update the run counter."""
    count = 1
    if os.path.exists(counter_file_path):
        with open(counter_file_path, "r") as file:
            count = int(file.read()) + 1
    with open(counter_file_path, "w") as file:
        file.write(str(count))
    return count

@contextmanager
def execute_command(command):
    """Execute a command and yield its stdout and stderr."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate()
        yield stdout, stderr
    finally:
        process.terminate()

def execute_and_log(command, output_file):
    """Execute a command and log its output."""
    print("#" * 90)
    print(f"Executing: {command}")
    print("#" * 90 + "\n")
    output_file.write("#" * 90 + "\n")
    output_file.write(f"Executing: {command}\n")
    output_file.write("#" * 90 + "\n\n")

    with execute_command(command) as (stdout, stderr):
        if stdout:
            output = stdout.decode()
            print(output)
            output_file.write(output + "\n")
        if stderr:
            output = stderr.decode()
            print(output)
            output_file.write(output + "\n")

    output_file.flush()

def create_app_commands():
    """Generate commands to create and set up the app."""
    if not os.path.exists(f'./{app_name}'):
        return [f'{npx_path} create-next-app {app_name} --js --tailwind --eslint --app --src-dir --import-alias "@/*" --yes']
    return ["echo 'app already created'"]

def install_packages_commands(packages):
    """Generate commands to install npm packages."""
    commands = []
    for pack in packages:
        if not is_package_installed_in_next_app(app_name, pack):
            commands.append(f"cd {app_name} && {npm_path} install --save {pack}")
        else:
            commands.append(f"echo '{pack} is already installed'")
    return commands

def update_gitignore(filepath, gitignore_path):
    """Add a filepath to .gitignore."""
    try:
        if not os.path.isfile(gitignore_path):
            with open(gitignore_path, 'w') as file:
                pass
        with open(gitignore_path, 'r') as file:
            if filepath in file.read():
                print(f"'{filepath}' is already in .gitignore")
                return
        with open(gitignore_path, 'a') as file:
            file.write(f"\n{filepath}")
            print(f"Added '{filepath}' to .gitignore")
    except Exception as e:
        print(f"An error occurred: {e}")

def execute_commands():
    """Main function to execute commands."""

    subprocess.run(f"rmdir /s /q {app_name}", shell=True)

    ensure_folder_exists('./prompts')

    run_counter_file = "./run_counter.txt"  # Path to your run counter file
    run_count = read_and_update_run_counter(run_counter_file)
    print(f"Run Count: {run_count}")

    with open("./prompts/output.log", "w") as output_file:
        commands = []

        if not check_venv_active():
            commands.append(f"{sys.executable} -m venv {venv_name}" if not os.path.exists(f'./{venv_name}') else "echo 'venv already created'")

        if not check_db_service("flex_development"):
            print(f"Please ensure the 'database' server is running")
            return

        if not is_package_installed("mysql"):
            commands.append(f"{sys.executable} -m pip install mysql-connector")

        commands.extend(create_app_commands())

        packages = [
            'react-dropdown-tree-select',
            '@reduxjs/toolkit',
            'next-auth',
            'bcrypt',
            'jsonwebtoken',
            'mysql2',
            'nodemailer',
            'react-redux',
            'redux',
            'redux-persist',
            'redux-thunk',
            'sequelize',
            'sequelize-cli',
            'react-youtube',
            'react-icons'
        ]

        commands.extend(install_packages_commands(packages))

        if os.path.exists(os.path.join(app_name, 'src/public')):
            for file in [file for file in os.listdir(os.path.join(app_name, 'src/public')) if file.endswith('.gguf')]:
                filepath = os.path.join(app_name, 'src/public', file)
                update_gitignore(filepath, os.path.join(app_name, '.gitignore'))

        additional_commands = [
            f'{sys.executable} Bot/build/code/cli/next/utils/nextBuilder/setup.py',
            f'cd {app_name}/src && {npx_path} sequelize-cli init',
            f'{sys.executable} Bot/build/code/cli/next/utils/api/nextdb.py',
            f'{sys.executable} Bot/build/code/cli/next/utils/api/nextapi.py',
            f'{sys.executable} Bot/build/code/cli/next/utils/api/nextui.py',
            f'{sys.executable} Bot/build/code/cli/next/info/add_path.py',
            f'{sys.executable} Bot/build/code/cli/next/info/code_cleaner.py',
            f'{sys.executable} Bot/build/code/cli/next/info/line_cleaner.py',
            f'cd {app_name} && code .'
        ]
        commands.extend(additional_commands)

        if run_count % 10 == 0:
            commands.append("echo 'Running extra commands because this is the 10th run'")

        for command in commands:
            execute_and_log(command, output_file)

if __name__ == "__main__":
    
    execute_commands()
