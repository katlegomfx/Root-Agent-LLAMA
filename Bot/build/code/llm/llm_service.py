# Bot\build\code\llm\llm_service.py
# llm_service.py
from colorama import Fore, Style

from typing import List, Dict, Any

from Bot.build.code.cli.cli_helpers import colored_print, strip_model_escapes

class LLMService:
    def __init__(self, client, model: str):
        """
        Initialize the service with a dependency-injected client.

        Args:
            client: An instance that implements the chat API (e.g., AsyncClient).
            model (str): The model identifier.
        """
        self.client = client
        self.model = model

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Send messages to the LLM and stream the response.

        Args:
            messages (List[Dict[str, str]]): List of messages to send.

        Returns:
            str: The complete assistant response.
        """
        print(f"#"*75)
        response = ""
        # Assume self.client.chat is an async iterator
        async for part in await self.client.chat(model=self.model, messages=messages, stream=True):
            section = part['message']['content']
            response += part['message']['content']
            section_clean = strip_model_escapes(section)
            colored_print(section_clean, color=Fore.YELLOW, end='', flush=True)
        print()
        return response
