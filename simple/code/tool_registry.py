import os
import glob
import inspect
import importlib.util
from typing import Dict, Callable

def load_custom_tools(custom_dir: str = os.path.join("simple", "code", "custom")) -> Dict[str, Callable]:
    """
    Scans the provided directory for Python files, imports them, and returns a registry
    of functions that accept an 'instruction' parameter.
    
    Args:
        custom_dir (str): The folder to scan for custom tool modules.
        
    Returns:
        Dict[str, Callable]: A dictionary mapping function names to functions.
    """
    registry = {}
    py_files = glob.glob(os.path.join(custom_dir, "*.py"))
    for file in py_files:
        module_name = os.path.splitext(os.path.basename(file))[0]
        spec = importlib.util.spec_from_file_location(module_name, file)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name, func in inspect.getmembers(module, inspect.isfunction):
            sig = inspect.signature(func)
            if "instruction" in sig.parameters:
                registry[name] = func
    return registry

def get_tool_registry() -> Dict[str, Callable]:
    """
    Automatically builds a tool registry by merging tools from function_call.py (loaded directly from file)
    and any custom tools found in 'simple/code/custom'. Only functions that accept an
    'instruction' parameter are registered.
    
    Returns:
        Dict[str, Callable]: A registry of tool functions.
    """
    registry = {}
    # Load built-in tools from function_call.py directly from file
    function_call_path = os.path.join("simple", "code", "function_call.py")
    spec = importlib.util.spec_from_file_location("function_call", function_call_path)
    if spec is not None and spec.loader is not None:
        function_call_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(function_call_module)
        for name, func in inspect.getmembers(function_call_module, inspect.isfunction):
            sig = inspect.signature(func)
            if "instruction" in sig.parameters:
                registry[name] = func

    # Merge with custom tools
    custom_registry = load_custom_tools()
    registry.update(custom_registry)
    return registry


tool_registry = get_tool_registry()
