import base64
import os
import time

import PIL.Image
from google import genai
from google.genai import types


from dotenv import load_dotenv
load_dotenv()


def generate_text():
    client = genai.Client(
        api_key=os.environ.get("gemini_key"),
    )

    model = "gemini-2.5-pro-exp-03-25"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Best ways to make money online."""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")


def inference_image():
    client = genai.Client(
        api_key=os.environ.get("gemini_key"),
    )

    model = "gemini-2.5-pro-exp-03-25"
    organ = PIL.Image.open("organ.jpg")
    contents = [
        types.Content(
            role="user",
            parts=["Tell me about this instrument", organ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")


def generate_audio():
    client = genai.Client(
        api_key=os.environ.get("gemini_key"),
    )

    model = "gemini-2.5-pro-exp-03-25"
    sample_audio = client.files.upload(file="sample.mp3")
    contents = [
        types.Content(
            role="user",
            parts=["Give me a summary of this audio file.", sample_audio],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")


def generate_video():
    client = genai.Client(
        api_key=os.environ.get("gemini_key"),
    )

    model = "gemini-2.5-pro-exp-03-25"
    myfile = client.files.upload(file="Big_Buck_Bunny.mp4")

    while myfile.state.name == "PROCESSING":
        print("processing video...")
        time.sleep(5)
        myfile = client.files.get(name=myfile.name)

        
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text="""Best ways to make money online."""), types.Part.from_video(myfile)
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")


def chat():
    client = genai.Client(
        api_key=os.environ.get("gemini_key"),
    )

    model = "gemini-2.5-pro-exp-03-25"


    chat = client.chats.create(
        model=model,
        history=[
            types.Content(role="user", parts=[types.Part(text="Hello")]),
            types.Content(
                role="model",
                parts=[
                    types.Part(
                        text="Great to meet you. What would you like to know?"
                    )
                ],
            ),
        ],
    )
    response = chat.send_message_stream(message="I have 2 dogs in my house.")
    for chunk in response:
        print(chunk.text)
        print("_" * 80)
    response = chat.send_message_stream(message="How many paws are in my house?")
    for chunk in response:
        print(chunk.text)
        print("_" * 80)

    print(chat.get_history())

if __name__ == "__main__":
    generate_text()
