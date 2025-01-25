# checkImageSystem.py

import asyncio
from Bot.build.code.llm.llm_client import see
import os
import PIL
from PIL import ImageGrab


def take_screenshot(filename):
    # Take a screenshot of the entire screen
    img = ImageGrab.grab()

    # Save the screenshot to a file
    img.save(filename)


# Specify the filename and path for the screenshot
filename = "screenshot.png"
path = "./screenshots"

full_path = os.path.join(path, filename)

# Ensure the directory exists, create if not
if not os.path.exists(path):
    os.makedirs(path)

# Take the screenshot and save it
take_screenshot(full_path)

print(f"Screenshot saved as {full_path}")



def handle_request():
    messages = [{
        'role': 'user',
        'content': 'What is in this image?',
        'images': [full_path]
    }]
    print(see(messages))

handle_request()



