import asyncio
import configparser
import re
from ollama import AsyncClient
import traceback
import time
import os
import json
import subprocess
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

from contextlib import suppress
from threading import Event

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout


load_dotenv()

assistant_prefix = 'assistant_resposne'
code_prefix = 'assistant_code'

ai_code_path = 'gen_ai_code'
ai_errors_path = 'gen_ai_errors'
ai_results_path = 'gen_ai_results'

anonymised = os.getenv('anonymised') if os.getenv('anonymised') else ''

error_file = 'currentError.txt'
triple_backticks = '`'*3

config = configparser.ConfigParser()
config.read("config.ini")

os.makedirs(ai_code_path, exist_ok=True)
os.makedirs(ai_errors_path, exist_ok=True)
os.makedirs(ai_results_path, exist_ok=True)


def read_file_content(path: str) -> str:
    """Reads and returns the entire content of the given file path as a string."""
    with open(path, 'r') as f:
        return "".join(f.readlines())


def write_content_to_file(content: str, path: str) -> None:
    """Writes the given content to a file at the specified path."""
    with open(path, 'w') as f:
        f.write(content)


def get_next_filename_index(directory: str, prefix: str) -> int:
    """
    Returns the next available file index in the given directory for files 
    starting with the given prefix.
    """
    return len([item for item in os.listdir(directory) if item.startswith(prefix)])


async def chat(messages: List[Dict[str, str]]) -> str:
    """
    Sends a list of messages to the AsyncClient and streams the assistant response.
    """
    assistant_response = ''
    # Directly iterate over the async iterator returned by AsyncClient().chat(...)
    client = AsyncClient()
    response_generator = await client.chat(model='llama3.2', messages=messages, stream=True)
    async for part in response_generator:
        section = part['message']['content']
        print(section, end='', flush=True)
        assistant_response += section
    print()
    return assistant_response


def extract_code(text: str, language: str = 'python') -> list[str]:
    """
    Extracts code blocks of the specified programming language from the given text.
    
    Parameters:
        text (str): The full text possibly containing code blocks.
        language (str): The language to look for in triple-backtick code fences.

    Returns:
        List[str]: A list of code block strings.
    """
    
    base_pattern = rf'{triple_backticks}{language}(.*?){triple_backticks}'
    code_blocks = re.findall(base_pattern, text, re.DOTALL)
    return code_blocks


def execute_tool(instuction: Dict[str, str]):
    """
    Send data to the tools and get the result back.
    run_bash_command
    run_web_scrape_command
    
    Parameters:
        message (Dict[str, str]): A dictionary containing the user message.
    
    Returns:
        Results from the command
    """
    if instuction['tool'] == run_bash_command.__name__:
        instuction = instuction['parameters']
        print(f"Executing command: {instuction}")
        return run_bash_command(instuction)

    elif instuction['tool'] == run_web_scrape_command.__name__:
        instuction = instuction['parameters']
        print(f"Executing command: {instuction}")
        return run_web_scrape_command(instuction)

    else:
        print(f"Tool {instuction['tool']} not found")
        return None    

  
async def process_user_messages_with_model(messages: List[Dict[str, str]], tool_use: bool = False, execute: bool = False) -> None:
    """
    Processes user messages with the Ollama model. Depending on the parameters, it may extract code blocks 
    (either JSON for tools or Python code), run commands, and store results and metadata.

    Parameters:
        messages (List[Dict[str, str]]): A list of messages for the model, each message containing a role and content.
        tool_use (bool): If True, treats the response as a JSON tool instruction block.
        execute (bool): If True, executes the code instructions in the JSON response (not yet implemented).

    Returns:
        None
    """
    try:
        start_time = time.time()
        assistant_response = await chat(messages)
        time_taken = time.time() - start_time
        executions = []
        if tool_use:
            codes = extract_code(assistant_response, language='json')
            # executions =  []
            for code in codes:
                json_instruct = json.loads(code)
                print(json.dumps(json_instruct, indent=4))

                if execute:
                    confirm = input(
                        f"Are you sure you want to execute the tool? (y/n): ")
                    while confirm.lower() not in ['y', 'n']:
                        confirm = input("Please enter y or n: ")

                    if confirm.lower() == 'y':
                        # Execute the tool
                        print(f"Executing tool: {json_instruct}")
                        executions.append(execute_tool(json_instruct))    

        else:
            codes = extract_code(assistant_response)
            number_of_files = get_next_filename_index(ai_code_path, code_prefix)
            for code in codes:
                write_content_to_file(code, os.path.join(
                    ai_code_path, f'{code_prefix}{number_of_files}.py'))

        request_info = {
            'input': {
                'instructions': messages[0]['content'],
                'prompt': messages[-1]['content']
            },
            'output': {
                'response': assistant_response,
                'code': codes
            },
            'processing': {
                'time_taken': time_taken,
                
            }
        }

        if executions != []:
            request_info['processing']['executions'] = executions

        json_request_info = json.dumps(request_info, indent=4)

        number_of_files = get_next_filename_index(ai_results_path, assistant_prefix)
        write_content_to_file(json_request_info, os.path.join(
            ai_results_path, f'{assistant_prefix}{number_of_files}.json'))

    except Exception as e:
        error_content = 'An error ocurred:\n'
        error_content += traceback.format_exc().replace(anonymised, '')
        write_content_to_file(
            error_content, os.path.join(ai_errors_path, error_file))

        print(f'An error ocurred:\n{e}')


def run_bash_command(command: str) -> str:
    """
    Runs a bash command and returns its output.

    Parameters:
        command (str): The bash command to be executed.

    Returns:
        str: The output of the executed bash command.
    """
    try:
        result = subprocess.run(command, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}"


def run_web_scrape_command(url: str) -> str:
    """
    Runs a web scrape command and returns its output.

    Parameters:
        url (str): The URL to be scraped.

    Returns:
        str: The content of the specified URL.
    """
    try:
        response = requests.get(url, timeout=5)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

def init_messages() -> (List[Dict[str, str]], List[Dict[str, str]]): # type: ignore
    """
    Initializes the message contexts for both general messages and tool messages.

    Returns:
        (List[Dict[str, str]], List[Dict[str, str]]): A tuple containing two lists of messages.
    """
    base_general_messages = [
        {'role': 'system', 'content': 'You are an expert python developer'}
    ]

    hard_coded = f"# You are an AI system, running on a windows machine"
    hard_coded += f"""
# Avaliable Tool:
## Name: 
[
    {run_bash_command.__name__},
    {run_web_scrape_command.__name__}
]
## Doc: 
[
    {run_bash_command.__doc__},
    {run_web_scrape_command.__doc__}
]
## Usage:
- Provide a JSON response wrapped in triple backticks and json
- The response should contain the tool name and parameter values
- Example
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

    return base_general_messages, base_tool_messages


class CLIApplication:
    def __init__(self):
        self.session = PromptSession()
        self.stop_event = Event()

        self.config = config

        self.timeout = self.config.getint("Settings", "timeout", fallback=160)
        prompt_style_str = self.config.get(
            "Styles", "prompt_style", fallback="bold #00ff00"
        )
        self.style = Style.from_dict(
            {
                "prompt": prompt_style_str,
            }
        )

        self.default_option = self.config.get(
            "Options", "default_option", fallback="option1"
        )

        self.background_interval = self.config.getint(
            "BackgroundTask", "interval", fallback=600
        )

        self.initial_messages: List[Dict[str, str]] = []
        self.initial_tool_messages: List[Dict[str, str]] = []

    async def run(self) -> None:
        messages = self.initial_messages.copy()
        tool_messages = self.initial_tool_messages.copy()

        while not self.stop_event.is_set():
            try:
                with patch_stdout():
                    try:
                        user_input = await self.session.prompt_async(
                            "> ",
                            completer=None,
                            complete_while_typing=False,
                            style=self.style,
                        )
                    except asyncio.TimeoutError:
                        print("\nTimed out!")
                        continue

            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                self.stop_event.set()
                break

            if not user_input or user_input.startswith('exit'):
                if user_input.startswith('exit'):
                    print('Goodbye')
                break

            if user_input.startswith('clear'):
                messages, tool_messages = init_messages()
                print("Clearing previous inputs")

            elif user_input.startswith('self'):
                base_code = read_file_content('main.py')
                user_request = user_input.replace('self ', '')
                prompt = f'# Considering the following: \n\n{
                    base_code}\n\n# {user_request})'
                messages.append({'role': 'user', 'content': prompt})
                await process_user_messages_with_model(messages)

            elif user_input.startswith('fix'):
                base_code = read_file_content('main.py')
                error_code = read_file_content(
                    os.path.join(ai_errors_path, error_file))
                user_request = user_input.replace('fix ', '')
                prompt = f'# Considering the following:\n\n{
                    base_code}\n\n# What modifications need to be made in order to address the error:\n\n{error_code}'
                messages.append({'role': 'user', 'content': prompt})
                await process_user_messages_with_model(messages)

            elif user_input.startswith('tool'):
                user_input = user_input.replace('tool ', '')
                prompt = user_input
                tool_messages.append({'role': 'user', 'content': prompt})
                await process_user_messages_with_model(
                    tool_messages, tool_use=True, execute=True)

            else:
                prompt = user_input
                messages.append({'role': 'user', 'content': prompt})
                await process_user_messages_with_model(messages)

    async def background_task(self, interval):
        try:
            while not self.stop_event.is_set():
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Background task error: {e}")


async def score_interaction(instructions: str, prompt: str, response: str) -> Dict[str, Any]:
    """
    Sends instructions, prompt, and response to the model and asks it to score them 
    in two categories: integration and conversation. Returns the parsed scores.
    """
    triple_backticks = '`'*3
    scoring_prompt = f"""
Consider the following interaction:

Instructions: {instructions}
Prompt: {prompt}
Response: {response}

Please score this triple on two categories using a scale from 1 to 10 (1 = poor, 10 = excellent):

1. Integration: How well does the response integrate with the instructions and the prompt?
2. Conversation: How well does the response engage in a coherent conversation?

Return your answer in JSON format only, like this:

{triple_backticks}json
{{
  "integration": <score>,
  "conversation": <score>
}}
{triple_backticks}
"""

    scoring_messages = [
        {"role": "system", "content": "You are an expert evaluator."},
        {"role": "user", "content": scoring_prompt}
    ]

    scoring_response = await chat(scoring_messages)

    try:
        scores = re.findall(
            r'```json\s*(\{.*?\})\s*```', scoring_response, re.DOTALL)
        if scores:
            data = json.loads(scores[0])
            return data
    except Exception:
        pass

    return {"integration": None, "conversation": None}


def load_history():
    files = [f for f in os.listdir(ai_results_path) if f.startswith(
        assistant_prefix) and f.endswith('.json')]
    files.sort()

    history_data = []
    for file_name in files:
        file_path = os.path.join(ai_results_path, file_name)
        with open(file_path, 'r') as f:
            data = json.load(f)
            instructions = data.get('input', {}).get('instructions', 'N/A')
            prompt = data.get('input', {}).get('prompt', 'N/A')
            response = data.get('output', {}).get('response', 'N/A')
            history_data.append((instructions, prompt, response))
    return history_data


async def summarize_interactions(top_interactions: List[Dict[str, Any]]) -> str:
    """
    Given top scored interactions, ask the model to produce a concise summary.
    """
    description = ""
    for i, inter in enumerate(top_interactions, start=1):
        description += f"Interaction {i}:\nInstructions: {inter['instructions']}\nPrompt: {inter['prompt']}\nResponse: {
            inter['response']}\nScores: Integration={inter['integration']}, Conversation={inter['conversation']}\n\n"

    summarize_prompt = f"""
You are a summarizer. Given these top interactions with their scores, produce a concise summary that captures the essence of how well the system is integrating instructions and maintaining coherent conversation. Keep it short and informative.

{description}
"""
    summarize_messages = [
        {"role": "system", "content": "You are an expert summarizer."},
        {"role": "user", "content": summarize_prompt}
    ]
    summary = await chat(summarize_messages)
    return summary.strip()


def cleanup_low_scores(scored_results: List[Dict[str, Any]], files: List[str]) -> (List[Dict[str, Any]], int): # type: ignore
    """
    If the number of files exceeds 'overall_limit', remove the bottom 'clean_up_percentage'% of scored results.
    Returns the cleaned list and updates overall_limit to clean_up_limit.
    """
    global overall_limit

    if len(scored_results) > overall_limit:
        # Calculate how many to remove
        to_remove_count = int(
            (clean_up_percentage / 100.0) * len(scored_results))
        if to_remove_count <= 0:
            return scored_results, overall_limit

        # Sort ascending by combined_score to remove lowest
        scored_results.sort(key=lambda x: x['combined_score'])
        to_remove = scored_results[:to_remove_count]
        # Remove the lowest scored files
        for item in to_remove:
            filename = item['file_name']
            file_path = os.path.join(ai_results_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)

        # Keep the rest
        scored_results = scored_results[to_remove_count:]

        # Update the overall_limit to clean_up_limit after first cleanup
        overall_limit = clean_up_limit

    return scored_results, overall_limit


async def main():
    cli_app = CLIApplication()

    # Load previous instructions/prompt/response sets with filenames
    # now returns (file_name, instructions, prompt, response)
    previous_data = load_history()
    scored_results = []
    base_messages, tool_messages = init_messages()

    # Score each triple and store filename
    for (file_name, instructions, prompt, response) in previous_data:
        scores = await score_interaction(instructions, prompt, response)
        integration = scores.get('integration', 0) or 0
        conversation = scores.get('conversation', 0) or 0
        combined_score = integration + conversation
        scored_results.append({
            'file_name': file_name,
            'instructions': instructions,
            'prompt': prompt,
            'response': response,
            'integration': integration,
            'conversation': conversation,
            'combined_score': combined_score
        })

    # Cleanup if we exceed overall_limit
    scored_results, current_limit = cleanup_low_scores(
        scored_results, [d[0] for d in previous_data])

    # Sort by combined score descending and keep top 10 for summary
    scored_results.sort(key=lambda x: x['combined_score'], reverse=True)
    top_ten = scored_results[:10]

    # Summarize top 10
    summary = ""
    if top_ten:
        summary = await summarize_interactions(top_ten)

    # Build scored messages: start with a system message containing the summary
    scored_messages = []
    if summary:
        scored_messages.append({'role': 'system', 'content': summary})

    # Add top 10 interactions to messages
    for inter in top_ten:
        scored_messages.append(
            {'role': 'system', 'content': inter['instructions']})
        scored_messages.append({'role': 'user', 'content': inter['prompt']})
        scored_content = f"{inter['response']}\n\n[Scores]: Integration={
            inter['integration']}, Conversation={inter['conversation']}"
        scored_messages.append(
            {'role': 'assistant', 'content': scored_content})

    # If no interactions, just keep base messages
    if scored_messages:
        messages = base_messages + [m for m in scored_messages]
        cli_app.initial_messages = messages
        cli_app.initial_tool_messages = tool_messages
    else:
        cli_app.initial_messages, cli_app.initial_tool_messages = init_messages()

    # Write the top 10 scored results to a new file
    top_ten_data = {
        "summary": summary,
        "top_interactions": top_ten
    }
    write_content_to_file(json.dumps(top_ten_data, indent=4),
                          os.path.join(ai_results_path, 'top_ten_scored.json'))

    background = asyncio.create_task(
        cli_app.background_task(cli_app.background_interval)
    )
    try:
        await cli_app.run()
    finally:
        cli_app.stop_event.set()
        background.cancel()
        with suppress(asyncio.CancelledError):
            await background



if __name__ == "__main__":
    asyncio.run(main())
