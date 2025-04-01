from diffusers import StableDiffusionPipeline  # type: ignore
import torch  # type: ignore
from PIL import Image # type: ignore
import base64
from io import BytesIO
from google import genai
from google.genai import types # type: ignore
from dotenv import load_dotenv # type: ignore
import os
load_dotenv()


client = genai.Client(api_key=os.getenv('gemini_key'))


def edit_image(path, new_path):
    image = Image.open('gemini-native-image.png')


    text_input = ('Hi, This is a picture of a robot.'
                'Can you add a robot dog next to it?',)

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=[text_input, image],
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save(new_path)
            image.show()


def interpert_image(path):
   # Image to text
    image = Image.open(path)
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[image, "Tell me about this image"]
    )
    final = ''
    for chunk in response:
        section = chunk.text
        print(section, end="")
        final += section

    return final



def generate_image(prompt: str,
                   output_filename: str = "generated_image.png",
                   model_name: str = "runwayml/stable-diffusion-v1-5",
                   transparent: bool = False) -> None:
    """
    Generates an image from the given prompt using Stable Diffusion,
    optionally processes the image to remove a white background (making it transparent),
    saves it to the specified file, and displays the image.

    Args:
        prompt (str): The text prompt for image generation.
        output_filename (str, optional): The file path to save the generated image.
            Defaults to "generated_image.png".
        model_name (str, optional): The Hugging Face model identifier for Stable Diffusion.
            Defaults to "runwayml/stable-diffusion-v1-5".
        transparent (bool, optional): If True, processes the image to remove near-white pixels,
            making the background transparent. Defaults to False.
    """
    try:
        # text to image
        contents = prompt

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )

        for part in response.candidates[0].content.parts:
          if part.text is not None:
            print(part.text)
          elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save(output_filename)
            image.show()
    except Exception as e:
        # Load the Stable Diffusion pipeline
        pipe = StableDiffusionPipeline.from_pretrained(model_name)
        # Uncomment the following line to use GPU (if available)
        # pipe = pipe.to("cuda")  # or "cpu" if needed

        # Generate an image from the prompt
        image = pipe(prompt).images[0]

        if transparent:
            # Convert the image to RGBA to support transparency.
            image = image.convert("RGBA")
            # Process each pixel: if the RGB values are near white, set its alpha to 0.
            new_data = []
            for pixel in image.getdata():
                # Define threshold for white (adjust threshold as needed)
                if pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:
                    # Replace near-white with transparent
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(pixel)
            image.putdata(new_data)

        # Save and display the image
        image.save(output_filename)
        # image.show()


# Example usage:
if __name__ == "__main__":
    # Generate a Python logo for Pygame with transparent background:
    generate_image("Minimalistic Python logo for pygame with transparent background",
                   output_filename="pygame_python_logo.png",
                   transparent=True)

    # Generate a toolbox icon for Pygame with transparent background:
    generate_image("Modern toolbox icon for pygame with transparent background",
                   output_filename="pygame_toolbox.png",
                   transparent=True)
    
    generate_image("Generate a logo for an app called ",
                   output_filename="pygame_toolbox.png",
                   transparent=True)
