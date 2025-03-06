import os
import json
import unittest
import tempfile

from simple.code.history import HistoryManager


class TestHistoryManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for history files
        self.test_dir = tempfile.TemporaryDirectory()
        self.history_manager = HistoryManager(history_dir=self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_get_history_files_empty(self):
        files = self.history_manager.get_history_files()
        self.assertEqual(files, [])

    def test_save_and_load_history(self):
        test_history = [{'role': 'system', 'content': 'Test prompt'}]
        file_path = self.history_manager.save_history(test_history)
        self.assertTrue(os.path.exists(file_path))

        # Now load the history
        loaded_history = self.history_manager.load_history(
            os.path.basename(file_path))
        self.assertEqual(loaded_history, test_history)

    def test_delete_history(self):
        test_history = [{'role': 'system', 'content': 'Test prompt'}]
        file_name = "test_history.json"
        self.history_manager.save_history(test_history, filename=file_name)
        file_path = os.path.join(self.test_dir.name, file_name)
        self.assertTrue(os.path.exists(file_path))
        self.history_manager.delete_history(file_name)
        self.assertFalse(os.path.exists(file_path))


if __name__ == '__main__':
    unittest.main()
