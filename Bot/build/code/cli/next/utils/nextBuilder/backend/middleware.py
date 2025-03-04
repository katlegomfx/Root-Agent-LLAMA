# Bot\build\code\cli\next\utils\nextBuilder\backend\middleware.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_middleware_route  # nopep8

MIDDLEWARE = """
"""

def create_smtp_api():
    subdirectory = ""  # Define the subdirectory path
    create_middleware_route('auth', MIDDLEWARE, subdirectory)

if __name__ == "__main__":
    create_smtp_api()
