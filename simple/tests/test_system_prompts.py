import os
import unittest
import tempfile

from simple.code.system_prompts import DEFAULT_PROMPT_CONTENT, DEFAULT_PROMPT_FILE, SystemPromptManager


class TestSystemPromptManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for system prompts
        self.test_dir = tempfile.TemporaryDirectory()
        self.prompt_manager = SystemPromptManager(folder=self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_default_prompt_creation(self):
        default_path = os.path.join(self.test_dir.name, DEFAULT_PROMPT_FILE)
        self.assertTrue(os.path.exists(default_path))
        with open(default_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, DEFAULT_PROMPT_CONTENT)

    def test_save_and_load_prompt(self):
        new_prompt = "New system prompt content."
        prompt_name = "new_prompt.txt"
        saved_path = self.prompt_manager.save_prompt(
            new_prompt, prompt_name=prompt_name)
        self.assertTrue(os.path.exists(saved_path))

        loaded_content = self.prompt_manager.load_prompt(prompt_name)
        self.assertEqual(loaded_content, new_prompt)

    def test_delete_prompt(self):
        prompt_name = "delete_prompt.txt"
        new_prompt = "Prompt to delete."
        self.prompt_manager.save_prompt(new_prompt, prompt_name=prompt_name)
        file_path = os.path.join(self.test_dir.name, prompt_name)
        self.assertTrue(os.path.exists(file_path))
        self.prompt_manager.delete_prompt(prompt_name)
        self.assertFalse(os.path.exists(file_path))

    def test_delete_default_prompt(self):
        with self.assertRaises(ValueError):
            self.prompt_manager.delete_prompt(DEFAULT_PROMPT_FILE)


if __name__ == '__main__':
    unittest.main()
