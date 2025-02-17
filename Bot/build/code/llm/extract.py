# Bot\build\code\llm\extract.py
import re

from Bot.build.code.session.constants import triple_backticks
from typing import List, Dict, Any

def extract_code(text: str, language: str = 'python') -> List[str]:
    """
    Extracts code blocks of the specified programming language from the given text.

    Uses triple backticks and a language specifier, e.g. ```python ... ```.

    Parameters:
        text (str): The full text possibly containing code blocks.
        language (str): The language to look for in triple-backtick code fences.

    Returns:
        List[str]: A list of code block strings.
    """
    pattern = rf'{triple_backticks}{language}(.*?){triple_backticks}'
    code_blocks = re.findall(pattern, text, re.DOTALL)
    return code_blocks
