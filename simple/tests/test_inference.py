import asyncio
import unittest
from unittest.mock import patch
import tkinter as tk

from simple.code.inference import run_inference

{MD_HEADING} Dummy asynchronous client that returns a fixed response.


class DummyAsyncClient:
    async def chat(self, model, messages, stream):
        async def dummy_generator():
            yield {"message": {"content": "Hello"}}
            yield {"message": {"content": " World"}}
        return dummy_generator()


class TestInference(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.widget = tk.Text(self.root)

    def tearDown(self):
        self.root.destroy()

    @patch('simple.code.inference.AsyncClient', new=DummyAsyncClient)
    def test_run_inference(self):
        messages = [{'role': 'user', 'content': 'Test'}]
        result = run_inference(messages, self.widget, self.root, "llama3.2")
        self.assertEqual(result, "Hello World")


if __name__ == '__main__':
    unittest.main()
