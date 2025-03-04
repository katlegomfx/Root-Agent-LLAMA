import os
from datetime import datetime

DEFAULT_PROMPT_FILE = "flexi.txt"
DEFAULT_PROMPT_CONTENT = "You are Flexi💻AI. You think step by step, keeping key points in mind to solve or answer the request."


class SystemPromptManager:
    def __init__(self, folder="system_prompts"):
        self.folder = folder
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.ensure_default_prompt()

    def ensure_default_prompt(self):
        default_path = os.path.join(self.folder, DEFAULT_PROMPT_FILE)
        if not os.path.exists(default_path):
            with open(default_path, "w", encoding="utf-8") as f:
                f.write(DEFAULT_PROMPT_CONTENT)

    def list_prompts(self):
        self.ensure_default_prompt()
        return [f for f in os.listdir(self.folder) if f.endswith(".txt")]

    def load_prompt(self, filename):
        path = os.path.join(self.folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def save_prompt(self, content, prompt_name=""):
        if not prompt_name:
            prompt_name = f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        elif not prompt_name.endswith(".txt"):
            prompt_name += ".txt"
        path = os.path.join(self.folder, prompt_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def delete_prompt(self, filename):
        if filename == DEFAULT_PROMPT_FILE:
            raise ValueError("Cannot delete the default system prompt.")
        path = os.path.join(self.folder, filename)
        os.remove(path)
