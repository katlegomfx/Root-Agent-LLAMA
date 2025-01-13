### building\auto_start.pyimport sys
from control import is_package_installed, execute_and_log

with open("./prompt/auto_output.log", "w") as output_file:
    commands = []
    if not is_package_installed("mysql"):
        commands.append(f"{sys.executable} -m pip install mysql-connector")
        commands.append(f"{sys.executable} -m pip install ollama")
        commands.append(f"{sys.executable} -m pip install chromadb")
        commands.append(f"{sys.executable} -m pip install requests")
        commands.append(f"{sys.executable} -m pip install tqdm")
        commands.append(f"{sys.executable} -m pip install termcolor")
        commands.append(f"{sys.executable} -m pip install huggingface-hub")

    for command in commands:
        execute_and_log(command, output_file)
