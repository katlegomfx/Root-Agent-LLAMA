# ./simple/inference.py:
import asyncio
from ollama import AsyncClient
from colorama import Fore

# Global reference for the current inference session.
current_client = None


class InferenceClient:
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = AsyncClient()
        self.cancelled = False

    async def chat(self, messages, widget, root):
        response_generator = await self.client.chat(model=self.model_name, messages=messages, stream=True)
        full_text = ""

        def append_text(s):
            widget.insert("end", s)
            widget.see("end")

        print("#" * 75)
        async for part in response_generator:
            if self.cancelled:
                print("\nInference cancelled.")
                root.after(0, append_text, "\n[Inference cancelled]")
                break
            section = part["message"]["content"]
            full_text += section
            print(section, end="", flush=True)
            root.after(0, append_text, section)
        print("\n" + "#" * 75)
        return full_text

    def cancel(self):
        self.cancelled = True


def run_inference(messages, widget, root, model_name):
    global current_client
    client = InferenceClient(model_name)
    current_client = client  # Save reference for cancellation.
    result = asyncio.run(client.chat(messages, widget, root))
    return result
