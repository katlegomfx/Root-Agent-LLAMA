# Bot\build\code\llm\prompts.py
import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Any

from ollama import AsyncClient

from Bot.build.code.llm.llm_client import chat, process_user_messages_with_model
from Bot.build.code.tasks.run_commands import execute_bash_command, fetch_url_content

from Bot.build.code.session.constants import (
    code_prefix,
    assistant_prefix,
    summary_prefix,
    ai_code_path,
    ai_results_path,
    ai_history_path,
    ai_errors_path,
    ai_summaries_path,
    binary_answer,
    anonymised, error_file,
    triple_backticks, 
    md_heading,
    gen_ai_path
)

from Bot.build.code.tasks.base_execute import tool_registry

def load_message_template(sys_type: str = 'base', summary:str = '') -> List[Dict[str, Any]]:
    if sys_type .lower() == "base":
        
        message = [
            {
                'role': 'system',
                'content': f"""
{md_heading} You are Flexi, an advanced AI agent capable of reflection and tool usage.
{md_heading} You must handle user requests by reasoning step by step:
{md_heading} 1) Understand the user request.
{md_heading} 2) If a tool is needed, produce a JSON instruction for that tool (in triple backticks).
{md_heading} 3) If the tool fails, reflect on the error message, correct the tool parameters, and try again.
{md_heading} 4) Provide the final result or an explanation to the user.
{md_heading} You maintain memory of the conversation and can self-critique or revise your approach if needed.
"""}]

    elif sys_type == "bot":
        message = [
            {'role': 'system', 'content': '# You are a super helpful assistant that helps uses an in an AI to comeplete the user request'}
        ]
    
    elif sys_type == "tool":
        hard_coded = f"""{md_heading} You are Flexi, an advanced AI agent capable of reflection and tool usage.
{md_heading} You must handle user requests by reasoning step by step:
{md_heading} 1) Understand the user request.
{md_heading} 2) If a tool is needed, produce a JSON instruction for that tool (in triple backticks).
{md_heading} 3) If the tool fails, reflect on the error message, correct the tool parameters, and try again.
{md_heading} 4) Provide the final result or an explanation to the user.
{md_heading} You maintain memory of the conversation and can self-critique or revise your approach if needed.
{md_heading} You specalise in tool use requiring json output to execute.
{md_heading} You are able to help the user with anything.
{md_heading} You will use the avaliable tools"""
        hard_coded += f"""
{md_heading} Avaliable Tool:
{md_heading}{md_heading} Name:
[
    {"".join(toolname for toolname,
             toolfunction in tool_registry.items())}
]
{md_heading}{md_heading} Doc:
[
    {"".join(toolfunction.__doc__ for toolname,
                 toolfunction in tool_registry.items())}
]
{md_heading}{md_heading} Usage:
- Provide a **JSON** response wrapped in triple backticks and json
- The response should contain the tool name and parameter values
- Example:
    {triple_backticks}json
    {{
        tool: <name>,
        parameters: <[values]>
    }}
    {triple_backticks}
"""
        base_tool_messages = [
            {"role": 'system', "content": hard_coded}
        ]

        message = base_tool_messages

    elif sys_type == "work":
        message = [
            {'role': 'system', 'content': '# You are a super helpful assistant'}
        ]

    elif sys_type == "projectSteps":
        message = [
            {'role': 'system', 'content': '# You are a super helpful assistant'}
        ]
    elif sys_type == "projectTasks":
        message = [
            {'role': 'system', 'content': '# You are a super helpful assistant'}
        ]
    elif sys_type == "projectProcess":
        message = [
            {'role': 'system', 'content': '# You are a super helpful assistant'}
        ]

    elif sys_type == "summary":
        message = [
            {'role': 'system', 'content': '# You are a personal assistant.\n# You are tasked with extracting important information from given text\n# Only respond with summarised important information!'}
        ]

    elif sys_type not in ["tool", ]:
        message = [
            {'role': 'system',
                'content': f'# You are an expert {sys_type.capitalize()} Developer'}
        ]

    elif  summary != '':
        message = [{
            'role': 'system',
            'content': f"{message[0]['content']}\n{md_heading}{md_heading}"
        }]

    message = add_context_to_messages(message, summary)
    
    return message

def extract_ordered_list_with_details(text, typer="Step"):
    items = {}
    counter = 1
    current_item = None
    converted_text = text.split('\n')

    code_block = False
    current_code = []

    for line in converted_text:
        ### Check for step/task with numbering        
        if (("step" in line.lower() or "task" in line.lower()) and f"{counter}" in line) or f"{counter}." in line:
            ### Save the previous item if it exists            
            if current_item:
                if current_code:  # If there's a code block being captured, add it before saving the item
                    current_item["details"]["code"] = '\n'.join(current_code)
                    current_code = []
                items[f"{typer} {counter - 1}"] = current_item

            ### Start a new item            
            base_line = line.replace(f"Step {counter}: ", "").replace(
                f"{counter}. ", "").strip('**').strip()
            current_item = {"title": base_line,
                            "details": {"instructions": ""}}

            counter += 1

        ### Detect the start and end of a code block        
        elif "```" in line:
            if not code_block:  # Start of a code block
                code_block = True
            else:  # End of a code block
                code_block = False
                if current_code:
                    if "code" in current_item["details"]:
                        current_item["details"]["code"] += '\n'.join(
                            current_code) + "\n"
                    else:
                        current_item["details"]["code"] = '\n'.join(
                            current_code) + "\n"
                current_code = []

        ### If inside a code block, capture the code        
        elif code_block:
            current_code.append(line)

        ### If not a step and not in a code block, add to instructions        
        elif current_item is not None:
            if current_item["details"]["instructions"]:
                current_item["details"]["instructions"] += "\n"
            current_item["details"]["instructions"] += line.strip()

    ### Don't forget to add the last item    
    if current_item:
        if current_code:  # If there's a code block being captured, add it before saving the item
            if "code" in current_item["details"]:
                current_item["details"]["code"] += '\n'.join(current_code)
            else:
                current_item["details"]["code"] = '\n'.join(current_code)
        ### Only add the code key if it contains code        
        if "code" not in current_item["details"] or not current_item["details"]["code"].strip():
            current_item["details"].pop("code", None)
        items[f"{typer} {counter - 1}"] = current_item

    return items

async def get_summary_on_files():
    all_summaries = os.listdir(os.path.join(gen_ai_path, ai_summaries_path))
    all_history = [f for f in os.listdir(os.path.join(gen_ai_path, ai_results_path)) if f.startswith(
        assistant_prefix) and f.endswith('.json')]

    if len(all_summaries) >= 1 or len(all_history) >= 1:
        print('Thinking About The Past')
        latest_summary_datetime = '0'
        latest_summary_file = ''

        ### use all_summaries        
        all_summaries.sort()
        if len(all_summaries) >= 1:
            latest_summary_file = all_summaries[-1]
            latest_summary_datetime = latest_summary_file.split('_')[
                2].split('.')[0]

        ### use all_history        
        if latest_summary_datetime != '0':
            ### get history after specific date            
            valid_history_files = [f for f in all_history if f.split(
                '_')[2].split('.')[0] > latest_summary_datetime]
            valid_history_files.sort()
            ### get history before specific date           
            invalid_history_files = [f for f in all_history if f.split(
                '_')[2].split('.')[0] <= latest_summary_datetime]
            invalid_history_files.sort()
            ### clean up history before specified date            
            for file in invalid_history_files:
                shutil.move(os.path.join(gen_ai_path, ai_results_path, file),
                            os.path.join(gen_ai_path, ai_history_path, file))
        else:
            ### get all history if no specified date            
            valid_history_files = [f for f in all_history]
            valid_history_files.sort()

        history_data = []
        for file_name in valid_history_files:
            file_path = os.path.join(gen_ai_path, ai_results_path, file_name)
            with open(file_path, 'r') as f:
                data = json.load(f)
                instructions = data.get('input', {}).get('instructions', 'N/A')
                prompt = data.get('input', {}).get('prompt', 'N/A')
                response = data.get('output', {}).get('response', 'N/A')
                history_data.append({
                    'role': 'system',
                    'content': instructions
                })
                history_data.append({
                    'role': 'user',
                    'content': prompt
                })
                history_data.append({
                    'role': 'assistant',
                    'content': response
                })

        ### if summary and history exists        
        if latest_summary_file != '' and history_data != []:
            print('Consolidating Summaries and History')
            ### open file and read text            
            with open(os.path.join(gen_ai_path, ai_summaries_path, latest_summary_file), 'r') as f:
                latest_summary_text = "".join(f.readlines())
            summary_messages = load_message_template(sys_type='summary')
            full_text = f'# Important Information: \n{latest_summary_text}'
            full_text += "\n\n# Chat History:\n\n"
            for m in history_data:
                if m['role'] != 'system':
                    full_text += f"{m['role']}: \n{m['content']}\n\n"

            print('Rewriting Summary With New History')
            ### rewrite summary            
            summary_messages.append({
                'role': 'user', 'content': full_text
            })
            result = await chat(summary_messages)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            with open(os.path.join(gen_ai_path, ai_summaries_path, f'{summary_prefix}_{timestamp}.txt'), 'w') as f:
                f.write(result)

        ### if only summary exists        
        if latest_summary_file != '' and history_data == []:
            print('Consolidating Summary')
            ### open file and read text            
            with open(os.path.join(gen_ai_path, ai_summaries_path, latest_summary_file), 'r') as f:
                latest_summary_text = "".join(f.readlines())
            result = latest_summary_text

        ### if only summary exists        
        if history_data != [] and latest_summary_file == '':
            print('Consolidating Summary')
            full_text = "Chat History:\n\n"
            for m in history_data:
                if m['role'] != 'system':
                    full_text += f"{m['role']}: \n{m['content']}\n\n"

            print('Creating New Summary')
            ### create the new summary            
            summary_messages = load_message_template(sys_type='summary')
            summary_messages.append({
                'role': 'user', 'content': full_text
            })
            result = await chat(summary_messages)

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            with open(os.path.join(gen_ai_path, ai_summaries_path, f'{summary_prefix}_{timestamp}.txt'), 'w') as f:
                f.write(result)

async def get_message_context_summary(messages_context):
    summary_prompt_messages = load_message_template("summary")
    full_text = ""
    for msg in messages_context:
        role = msg['role']
        content = msg['content']
        if role != 'system':
            full_text += f"{role}: {content}\n\n"

    summary_prompt_messages.append({
        'role': 'user',
        'content': f"Summarize the important information:\n\n{full_text}"
    })

    summary_result = await process_user_messages_with_model(summary_prompt_messages)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    summary_filename = os.path.join(gen_ai_path, ai_summaries_path, f'{
                                    summary_prefix}_{timestamp}.md')
    with open(summary_filename, 'w') as f:
        f.write(summary_result)

    return summary_result

def get_py_files_recursive(directory, exclude_dirs=None, exclude_files=None):
    """
    Recursively searches for Python files (.py) in a given directory and its subdirectories,
    excluding specified directories and file names.

    Args:
        directory (str): The path to the root directory to search.
        exclude_dirs (list, optional): A list of directories to exclude from the search. Defaults to ['venv'].
        exclude_files (list, optional): A list of Python files (.py) to exclude from the search. Defaults to [].

    Returns:
        list: A list of paths to found Python files.
    """
    if exclude_dirs is None:
        exclude_dirs = ['venv']
    if exclude_files is None:
        exclude_files = []

    ### Note: This line was causing an error because dir[:] = ... does not modify the original dir variable    
    ### We need to use a new list instead    

    py_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py') and file not in exclude_files:
                py_files.append(os.path.join(root, file))

    return py_files

def code_corpus(path: str):
    """
    Reads the content of all Python files in a given directory.

    Args:
        path (str): The path to the root directory containing Python files.

    Returns:
        list: A list of strings representing the contents of each Python file.
    """
    exclude_files = [
        'craze.py',
        'ibot.py',
        'nextBuilderIntegration.py',

    ]
    exclude_dirs = [
        'interest',
        'pyds',
        'backup',
        'models',
        'sdlc',
        'self_autoCode',
        'self_autoCodebase',
        'tests',
        'to_confirm_tools',
        
    ]
    paths = get_py_files_recursive(
        path, exclude_dirs=exclude_dirs, exclude_files=exclude_files)
    current_project_item = []
    for file_path in paths:
        text = read_file_content(file_path)
        current_project_item.append(f'\n## {file_path}:\n{text}\n')
    return current_project_item

def read_file_content(path: str) -> str:
    """
    Reads and returns the entire content of a given file.

    Args:
        path (str): The path to the file to be read.

    Returns:
        str: The content of the specified file.
    """
    with open(path, 'r') as f:
        if path.endswith('.md') or path.endswith('.py'):
            return "".join(f.readlines()).replace('# ', '## ')
        else:
            return "".join(f.readlines()).replace('# ', '## ')

def add_context_to_messages(messages, context):
    for m in messages:
        if m['role'] == 'system':
            content = f"{m['content']}\n\n## Summary History\n\n{context}"
            messages = [{'role': 'system', 'content': content}]
    return messages
    

async def embedText(writtenText, model='nomic-embed-text'):

    client = AsyncClient()
    embedded_response = ''
    response_generator = await client.embed(model='llama3.2', input=writtenText, stream=True)
    async for part in response_generator:
        section = part['message']['content']
        ### print(section, end='', flush=True)            embedded_response += section
    print()
    return embedded_response
