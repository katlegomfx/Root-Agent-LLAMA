# llm.py
import re
import os
import sys
import json
import random
import asyncio
import traceback
from typing import Dict, Any, List

import colorama
from colorama import Fore, Style

from Bot.build.code.cli.cli_helpers import colored_print
from Bot.build.code.llm.prompts import load_message_template
from Bot.build.code.llm.workflows import code_use, decide_execution, tool_use
from Bot.build.code.tasks.base_execute import execute_code, execute_tool
from Bot.build.code.llm.llm_client import chat
from Bot.build.code.llm.extract import extract_code

colorama.init()

triple_backticks = '`' * 3
md_heading = "#"



os.makedirs('results', exist_ok=True)



async def versionOne(main_prompt):
    results_path = './results'
    os.makedirs(results_path, exist_ok=True)

    
    colored_print("Deciding using AI", Fore.GREEN)
    base_prompt = load_message_template()
    base_prompt.append(main_prompt)
    ai_choice = await decide_execution(base_prompt)
    if ai_choice == "python":
        colored_print("Starting Python Code Use", Fore.GREEN)
        base_prompt = load_message_template('python')
        base_prompt.append(main_prompt)
        final_response, code_script, status_message, base_prompt = await code_use(base_prompt)
        with open(os.path.join(results_path, 'code_model_output.md'), 'w', encoding='utf-8') as f:
            f.write(''.join(final_response))
        with open(os.path.join(results_path, 'code_generation_output.py'), 'w', encoding='utf-8') as f:
            f.write(''.join(code_script))
        with open(os.path.join(results_path, 'code_execution_output.json'), 'w', encoding='utf-8') as f:
            json.dump(status_message, f, indent=4)
        with open(os.path.join(results_path, 'code_chat_history.json'), 'w', encoding='utf-8') as f:
            json.dump(base_prompt, f, indent=4)
    elif ai_choice == "tool":
        colored_print("Starting Tool Use", Fore.GREEN)
        base_prompt = load_message_template('tool')
        base_prompt.append(main_prompt)
        base_response, code_script, status_message, base_prompt = await tool_use(base_prompt)
        with open(os.path.join(results_path, 'tool_model_output.md'), 'w', encoding='utf-8') as f:
            f.write(''.join(base_response))
        with open(os.path.join(results_path, 'tool_instruction_output.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(code_script, indent=4))
        with open(os.path.join(results_path, 'tool_execution_output.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(status_message, indent=4))
        with open(os.path.join(results_path, 'tool_chat_history.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(base_prompt, indent=4))
    else:
        colored_print("No valid option provided", Fore.CYAN)


def full_run():
    code_text = open("llm.py", "r", encoding="utf-8").read()
    my_list = [
        {
            "role": "user",
            "content": f"{md_heading} Write a python function to get the number of characters in a given file path"
        },
        {
            "role": "user",
            "content": f"{md_heading} Show me the files in the current directory"
        },
        {
            "role": "user",
            "content": f"{md_heading} show me who the current user of the computer is"
        }
    ]
    main_prompt = random.choice(my_list)
    try:
        asyncio.run(versionOne(main_prompt))
    except Exception as e:
        with open("error.log", "w", encoding="utf-8") as err_file:
            err_file.write("An unhandled error occurred:")
            traceback.print_exc(file=err_file)
        error_text = open("error.log", "r", encoding="utf-8").read()
        base_prompt = load_message_template('python')
        base_prompt.append({
            'role': 'user',
            'content': f"Look at the following error:\n{error_text}\nIn the code:\n{code_text}\nHow can we fix this error"
        })
        fix_res = asyncio.run(chat(base_prompt))
        open("error_fix.md", "w", encoding="utf-8").write(fix_res)
        sys.exit(1)
    finally:
        colored_print("Writing out some Code suggestions", Fore.GREEN)
        base_prompt = load_message_template('python')
        base_prompt.append({
            'role': 'user',
            'content': f"Look at the following error:\n{code_text}\nHow can we refactor the code to adhere to DRY principles?"
        })
        code_suggestions = asyncio.run(chat(base_prompt))
        open("code_suggestions.md", "w", encoding="utf-8").write(code_suggestions)


if __name__ == "__main__":
    full_run()

# - what do we need to do
# - what do we have that can do it
# - what can we build to do it
# - How do we do it
# - Do we need an executor (Python or Tools)
# - What instructions/code do you provide
# - What are the results of the execution
# - Is everything working correctly
# - (If error start this process again with error as prompt)
# - How do we optimize and improve