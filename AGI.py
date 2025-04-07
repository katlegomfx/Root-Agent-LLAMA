
import asyncio
import logging
import os
import ast
import glob
import importlib.util
from IPython import display
from typing import Dict, Callable, List

from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv()


os.environ['GOOGLE_API_KEY'] = os.getenv('gemini_key')
client = genai.Client(http_options= {
      'api_version': 'v1alpha'
})
model_name = "gemini-2.5-pro-exp-03-25"


logger = logging.getLogger('Live')
# logger.setLevel('DEBUG')
logger.setLevel('INFO')

MD_HEADING = "#"


async def handle_tool_call(session, tool_call, custom_functions):
  for fc in tool_call.function_calls:
    function_name = fc.name
    function_args = fc.args
    # Find the function object from the list based on the function name
    tool_response = types.LiveClientToolResponse(
        function_responses=[types.FunctionResponse(
            name=fc.name,
            id=fc.id,
            response={
                'result': custom_functions[function_name](**function_args)},
        )]
    )

    print('\n>>> ', tool_response)
    await session.send(input=tool_response)


def handle_server_content(server_content):
  model_turn = server_content.model_turn
  if model_turn:
    for part in model_turn.parts:
      executable_code = part.executable_code
      if executable_code is not None:
        display.display(display.Markdown('-------------------------------'))
        display.display(display.Markdown(f'``` python\n{executable_code.code}\n```'))
        display.display(display.Markdown('-------------------------------'))

      code_execution_result = part.code_execution_result
      if code_execution_result is not None:
        display.display(display.Markdown('-------------------------------'))
        display.display(display.Markdown(f'```\n{code_execution_result.output}\n```'))
        display.display(display.Markdown('-------------------------------'))

  grounding_metadata = getattr(server_content, 'grounding_metadata', None)
  if grounding_metadata is not None:
    display.display(
        display.HTML(grounding_metadata.search_entry_point.rendered_content))

  return


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

def get_all_tools_docs():
    """Gets list of tools if"""
    return [types.FunctionDeclaration.from_callable(
        callable=func, client=client).to_json_dict()
        for name, func in tool_registry.items()]


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
            # corpus.append(f'\n{MD_HEADING} {file_path}:\n{text}\n')
            corpus.append({file_path:text})
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    return corpus

tool_registry.update({code_corpus.__name__: code_corpus})



def get_tools_docs():
    """Gets list of tools that can be used"""
    base = [types.FunctionDeclaration.from_callable(
        callable=func, client=client).to_json_dict()
        for name, func in tool_registry.items() if name in ['write_custom_python_file', 'execute_bash_command', 'create_file', 'modify_file']]
    # base.append(types.FunctionDeclaration.from_callable(
    #     callable=get_tools_docs, client=client).to_json_dict())
    base.append(types.FunctionDeclaration.from_callable(
        callable=code_corpus, client=client).to_json_dict())

    return base




n = 0
custom_functions = tool_registry

async def run(prompt, modality="TEXT", tools=None):

    global n

    if tools is None:

        tools = []

    config = {


        "tools": tools,


        "response_modalities": [modality]}

    async with client.aio.live.connect(model=model_name, config=config) as session:

        display.display(display.Markdown(prompt))

        display.display(display.Markdown('-------------------------------'))

        await session.send(input=prompt, end_of_turn=True)

        async for response in session.receive():

            logger.debug(str(response))

            if text := response.text:

                display.display(display.Markdown(text))

                continue

            server_content = response.server_content

            if server_content is not None:

                handle_server_content(server_content)

                continue

            tool_call = response.tool_call

            if tool_call is not None:

                await handle_tool_call(session, tool_call, custom_functions)

        n = n+1


async def main():
    while True:
        tools = [
            {'google_search': {}},
            {'code_execution': {}},
            {'function_declarations': get_tools_docs()}
        ]
        corpus = code_corpus('./web/build')

        try:
            user_prompt = input(
                "\nEnter your prompt (press Enter or type 'exit' to quit): ")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received. Exiting.")
            break

        if not user_prompt.strip() or user_prompt.strip().lower() == "exit":
            print("Exiting.")
            break

        prompt = f'''# Considering the following:\n\n{corpus}{user_prompt}'''

        await run(prompt, tools=tools, modality="TEXT")


if __name__ == '__main__':
    asyncio.run(main())
