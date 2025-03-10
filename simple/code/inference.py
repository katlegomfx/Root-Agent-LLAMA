import asyncio
from typing import List, Any
from ollama import AsyncClient
import logging

logging.basicConfig(level=logging.INFO)

# Global reference for the current inference session.
current_client = None


class InferenceClient:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.client = AsyncClient()
        self.cancelled = False

    async def chat(self, messages: List[dict], widget: Any, root: Any) -> str:
        try:
            response_generator = await self.client.chat(model=self.model_name, messages=messages, stream=True)
        except Exception as e:
            logging.error(f"Error starting chat: {e}")
            return f"Error starting inference: {e}"

        full_text = ""

        def append_text(s: str) -> None:
            widget.insert("end", s)
            widget.see("end")

        logging.info("Starting inference chat...")
        async for part in response_generator:
            if self.cancelled:
                logging.info("Inference cancelled.")
                root.after(0, append_text, "\n[Inference cancelled]")
                break
            section = part.get("message", {}).get("content", "")
            full_text += section
            print(section, end="", flush=True)
            root.after(0, append_text, section)
        logging.info("Inference completed.")
        return full_text

    def cancel(self) -> None:
        self.cancelled = True


def run_inference(messages: List[dict], widget: Any, root: Any, model_name: str) -> str:
    global current_client
    client = InferenceClient(model_name)
    current_client = client  # Save reference for cancellation.
    try:
        result = asyncio.run(client.chat(messages, widget, root))
    except Exception as e:
        logging.error(f"Error during inference: {e}")
        result = f"Error during inference: {e}"
    return result
