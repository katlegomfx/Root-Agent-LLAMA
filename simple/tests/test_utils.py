import os
import unittest
import tempfile

from simple.code import utils


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory with some dummy Python files
        self.test_dir = tempfile.TemporaryDirectory()
        self.file1_path = os.path.join(self.test_dir.name, "file1.py")
        self.file2_path = os.path.join(self.test_dir.name, "file2.py")
        with open(self.file1_path, "w", encoding="utf-8") as f:
            f.write("print('Hello from file1')")
        with open(self.file2_path, "w", encoding="utf-8") as f:
            f.write("print('Hello from file2')")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_get_py_files_recursive(self):
        py_files = utils.get_py_files_recursive(self.test_dir.name)
        self.assertIn(self.file1_path, py_files)
        self.assertIn(self.file2_path, py_files)

    def test_read_file_content(self):
        content = utils.read_file_content(self.file1_path)
        self.assertIn("Hello from file1", content)

    def test_code_corpus(self):
        corpus = utils.code_corpus(self.test_dir.name)
        self.assertTrue(any("file1.py" in entry for entry in corpus))
        self.assertTrue(any("file2.py" in entry for entry in corpus))


if __name__ == '__main__':
    unittest.main()
