import re

from Bot.build.code.session.constants import triple_backticks
from typing import List, Dict, Any

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

