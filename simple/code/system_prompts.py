import importlib.util
from typing import List, Dict
import inspect
from simple.code.logging_config import setup_logging
from simple.code.tool_registry import tool_registry, get_tool_docs
setup_logging()

thesysname = "You are Flexi💻AI."
DEFAULT_PROMPT_FILE = "flexi.txt"
DEFAULT_PROMPT_CONTENT = f"{thesysname}. You think step by step, keeping key points in mind to solve or answer the request."
MD_HEADING = "#"
TRIPLE_BACKTICKS = "```"


def add_context_to_messages(messages: List[Dict[str, str]], summary: str) -> List[Dict[str, str]]:
    """
    Appends a summary context to each system message if provided.
    """
    if summary:
        for msg in messages:
            if msg.get('role') == 'system':
                msg['content'] += f"\n\nSummary Context:\n{summary}"
    return messages


def load_message_template(sys_type: str = 'base', summary: str = '') -> List[Dict[str, str]]:
    sys_type = sys_type.lower()
    tool_docs = get_tool_docs()
    tool_names = list(tool_docs.keys())
    tool_documentation = [f"{name}: {doc}" for name, doc in tool_docs.items()]

    sys_type = sys_type.lower()
    if sys_type == "base":
        content = f"""
{MD_HEADING} {thesysname}, an advanced AI agent capable of reflection, code execution and tool usage.
{MD_HEADING} You must handle user requests by reasoning step by step:
- 1) Understand the user request.
- 2) Choose if you will use a tool or python.
{MD_HEADING} Respond with your choice in a JSON object wrapped in triple backticks.
{MD_HEADING} Usage:
- Provide a **JSON** response wrapped in triple backticks (starting with {TRIPLE_BACKTICKS}json).
- The response should contain the name of the executor to use (either "python" or "tool").
- Schema Example:
    {TRIPLE_BACKTICKS}json
    {{"use": "<name>"}}
    {TRIPLE_BACKTICKS}
- Example 1:
    {TRIPLE_BACKTICKS}json
    {{"use": "tool"}}
    {TRIPLE_BACKTICKS}
- Example 2:
    {TRIPLE_BACKTICKS}json
    {{"use": "python"}}
    {TRIPLE_BACKTICKS}
{MD_HEADING} Available Tools:
- Names: {", ".join(tool_names)}
- Documentation:
{chr(10).join(tool_documentation)}
"""
        message = [{'role': 'system', 'content': content.strip()}]
    elif sys_type == "answer":
        content = f"{MD_HEADING} {thesysname}, answer using only the provided information."
        message = [{'role': 'system', 'content': content.strip()}]
    elif sys_type == "check":
        content = f"""
{MD_HEADING} {thesysname}, determine if the user's request was fulfilled.
{MD_HEADING} Respond in a JSON object wrapped in triple backticks.
{MD_HEADING} Example:
    {TRIPLE_BACKTICKS}json
    {{"use": "yes"}}
    {TRIPLE_BACKTICKS}
"""
        message = [{'role': 'system', 'content': content.strip()}]
    elif sys_type == "tool":
        content = f"""
{MD_HEADING} {thesysname}, an advanced AI agent capable of reflection and tool usage.
{MD_HEADING} You must handle user requests by reasoning step by step:
1) Understand the user request.
2) If a tool is needed, output a JSON instruction (wrapped in triple backticks).
3) Do not show any expected output.
4) If execution fails, adjust parameters and try again.
{MD_HEADING} Respond with your choice in a JSON object wrapped in triple backticks.
{MD_HEADING} Usage:
- Provide a **JSON** response wrapped in triple backticks (starting with {TRIPLE_BACKTICKS}json).
{MD_HEADING} Available Tools:
- Names: {", ".join(tool_names)}
- Documentation:
{chr(10).join(tool_documentation)}
{MD_HEADING} Usage:
- Output a JSON response wrapped in triple backticks.
- Include the tool name and parameters.
Example:
    {TRIPLE_BACKTICKS}json
    {{"tool": "<name>", "parameters": "<values>"}}
    {TRIPLE_BACKTICKS}
"""
        message = [{'role': 'system', 'content': content.strip()}]
    elif sys_type == "summary":
        message = [{'role': 'system', 'content': f"{MD_HEADING} You are a personal assistant. Extract and summarize key points from the provided text."}]
    elif sys_type not in ["tool", ]:
        message = [
            {'role': 'system',
                'content': f'{MD_HEADING} You are an expert {sys_type.capitalize()} Developer'}
        ]
    else:
        message = [
            {'role': 'system', 'content': f"{MD_HEADING} You are an expert {sys_type.capitalize()} Developer."}]
    return add_context_to_messages(message, summary)
