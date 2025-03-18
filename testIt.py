import os
import glob
import ast
import importlib.util
from typing import Dict, Callable


def extract_functions_with_instruction(file_path: str) -> Dict[str, Callable]:
    with open(file_path, 'r', encoding='utf-8') as file:
        parsed = ast.parse(file.read(), file_path)

    functions = {}
    for node in ast.walk(parsed):
        print(type(node))
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
    print(os.listdir(custom_dir))
    registry = {}
    py_files = glob.glob(os.path.join(custom_dir, "*.py"))
    for file in py_files:
        registry.update(extract_functions_with_instruction(file))
    return registry


def load_builtin_tools() -> Dict[str, Callable]:
    builtin_path = os.path.join("simple", "code", "function_call.py")
    print(os.listdir(os.path.join("simple", "code")))
    return extract_functions_with_instruction(builtin_path)


def get_tool_registry() -> Dict[str, Callable]:
    registry = load_builtin_tools()
    registry.update(load_custom_tools())
    return registry


tool_registry = get_tool_registry()


def get_tool_docs():
    return {name: (func.__doc__ or "No documentation provided").strip()
            for name, func in tool_registry.items()}


print(tool_registry)