import base64
import os
import time
import ast
import glob
import importlib.util
from typing import Dict, Callable, List

from google import genai
from google.genai import types


from dotenv import load_dotenv
load_dotenv()

thesysname = "You are Flexi💻AI"
MD_HEADING = "#"


DEFAULT_SYS_PROMPT = f"""{thesysname}. You think step by step, keeping key points in mind to solve or answer the request."""


def create_prompt_item(request='snake in pygame', role='user'):
    a_prompt = types.Content(
        role=role,
        parts=[
            types.Part.from_text(
                text=f"""{MD_HEADING} Request: {request}""" if role == 'user' else request),
        ],
    )
    return a_prompt


DEFAULT_PROMPT = [create_prompt_item()]

client = genai.Client(
    api_key=os.environ.get("gemini_key"),

)


def extract_functions_with_instruction(file_path: str) -> Dict[str, Callable]:
    with open(file_path, 'r', encoding='utf-8') as file:
        parsed = ast.parse(file.read(), file_path)

    functions = {}
    for node in ast.walk(parsed):
        if isinstance(node, ast.FunctionDef):
            params = [arg.arg for arg in node.args.args]
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            spec = importlib.util.spec_from_file_location(
                module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                func = getattr(module, node.name, None)
                if callable(func):
                    functions[node.name] = func
    return functions


def load_custom_tools(custom_dir: str = os.path.join("simple", "code", "custom")) -> Dict[str, Callable]:
    registry = {}
    py_files = glob.glob(os.path.join(custom_dir, "*.py"))
    for file in py_files:
        registry.update(extract_functions_with_instruction(file))
    return registry


def load_builtin_tools() -> Dict[str, Callable]:
    builtin_path = os.path.join("simple", "code", "function_call.py")
    return extract_functions_with_instruction(builtin_path)


def get_tool_registry() -> Dict[str, Callable]:
    registry = load_builtin_tools()
    registry.update(load_custom_tools())
    return registry


tool_registry = get_tool_registry()


def code_corpus(directory: str) -> List[str]:
    """
    Builds a corpus by reading all Python, Typescript and Javascript files in the directory.
    """
    exclude_files = []
    exclude_dirs = [
        'idea',
        'imagev1',
        'models',
        'pretrained',
        'prompts',
        'pyds',
        'node_modules',
        '.next',
        '__pycache__'
    ]
    file_paths = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.split('.')[-1] in ['py', 'ts', 'tsx', 'js', 'jsx', 'md'] and file not in exclude_files:
                file_paths.append(os.path.join(root, file))

    corpus = []
    for file_path in file_paths:
        try:
            text = open(file_path, 'r', encoding='utf-8').read()
            corpus.append({file_path: text})
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    return corpus


tool_registry.update({code_corpus.__name__: code_corpus})


def get_tools_docs():
    """Gets list of tools that can be used"""
    base = [types.FunctionDeclaration.from_callable(
        callable=func, client=client).to_json_dict()
        for name, func in tool_registry.items() if name in ['write_custom_python_file', 'execute_bash_command', 'create_file', 'modify_file', 'code_corpus', 'read_file', 'delete_file', 'rename_move_file', 'list_directory_contents']]
    return base


# print()
# print(get_tools_docs())
# print()
# input()

def generate_text(prompt=DEFAULT_PROMPT, system_prompt=DEFAULT_SYS_PROMPT):
    model = "gemini-2.5-pro-exp-03-25"
    contents = prompt

    tools = {'google_search': {},
             'code_execution': {},
             'function_declarations': get_tools_docs()}

    response = ''
    function_response = []
    code_response = ''
    execution_response = ''
    candidate_response = ''
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt, tools=[tools]),
    ):

        if chunk.function_calls is not None:
            function_response = chunk.function_calls

        if chunk.executable_code is not None:
            code_response += chunk.executable_code

        if chunk.code_execution_result is not None:
            execution_response += chunk.code_execution_result

        if chunk.text is not None:
            response += chunk.text

        print(chunk.text, end="")
    print()

    return response, function_response


def handle_tool_call(tool_call, custom_functions):
    function_name = tool_call.name
    function_args = tool_call.args
    # Find the function object from the list based on the function name
    tool_response = types.Part.from_function_response(
        name=tool_call.name,
        response={
            'result': custom_functions[function_name](**function_args)},
    )

    print('\n>>> Tool Response:', tool_response)
    return tool_response


def chat_agent(request="I code in python and javascript.", history=[]):
    history.append(create_prompt_item(request, 'user'))
    response, function_calls = generate_text(history)
    for function_call in function_calls:
        history.append(types.Content(role="model", parts=[
            types.Part(function_call=function_call)]))
        tool_call = handle_tool_call(function_call, tool_registry)
        history.append(types.Content(
            role="user", parts=[tool_call]))
        response, function_calls = generate_text(history)

    return response, history


def chat_with_history(history=[], request="I code in python and javascript."):
    response, history = chat_agent(request=request, history=history)
    history.append(create_prompt_item(response, 'model'))

    return history


def main():
    new_history = []
    while True:
        corpus = code_corpus('./web/sites')
        try:
            user_prompt = input(
                "\n> ")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received. Exiting.")
            break

        if not user_prompt.strip() or user_prompt.strip().lower() == "exit":
            print("Exiting.")
            break

        prompt = f'''# Considering the following:\n\n{corpus}\n\n# Request:\n{user_prompt}'''
        # input(prompt)
        new_history = chat_with_history(new_history, request=prompt)


if __name__ == "__main__":
    main()
