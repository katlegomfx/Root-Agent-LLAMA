### building\auto_build.py

import sys
from control import is_package_installed, execute_and_log

with open("./prompt/auto_output.log", "w") as output_file:
    commands = []

    for command in commands:
        execute_and_log(command, output_file)
