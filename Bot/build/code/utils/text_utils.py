import re
from Bot.build.code.session.constants import triple_backticks

def strip_code_blocks(text: str) -> str:
    """
    Removes code blocks enclosed in triple backticks from the given text.

    Args:
        text (str): The input text containing potential code blocks.

    Returns:
        str: The text with code blocks removed.
    """
    pattern = rf'{re.escape(triple_backticks)}.*?{re.escape(triple_backticks)}'
    return re.sub(pattern, '', text, flags=re.DOTALL)
