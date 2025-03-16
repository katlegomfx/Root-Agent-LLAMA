import unittest
import tkinter as tk

from simple.code.agent_gui import FlexiAIApp

{MD_HEADING} Dummy manager classes to isolate the GUI tests from file I/O.


class DummyHistoryManager:
    def get_history_files(self):
        return []

    def save_history(self, history):
        pass


class DummySystemPromptManager:
    def list_prompts(self):
        return []


class TestFlexiAIApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = FlexiAIApp(self.root)
        self.app.history_manager = DummyHistoryManager()
        self.app.prompt_manager = DummySystemPromptManager()
        self.app.codebase_path_entry.delete(0, tk.END)
        self.app.codebase_path_entry.insert(0, "")
        self.app.tips_entry.delete("1.0", tk.END)
        self.app.tips_entry.insert("1.0", "Some additional tips")

    def tearDown(self):
        self.root.destroy()

    def test_build_full_prompt_without_codebase(self):
        user_request = "Solve the equation"
        full_prompt = self.app.build_full_prompt(user_request)
        self.assertIn(user_request, full_prompt)
        self.assertIn("Some additional tips", full_prompt)


if __name__ == '__main__':
    unittest.main()
