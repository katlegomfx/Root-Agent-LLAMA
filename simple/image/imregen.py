import numpy as np
from diffusers import StableDiffusionImg2ImgPipeline # type: ignore
import torch # type: ignore
from PIL import Image # type: ignore
import numpy as np # type: ignore

import os
import glob
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image

# Load the pipeline
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5")

path_loc = "simple/gag/generated_image.png"
# Load the image, convert to RGB, then to a numpy array
init_image = Image.open(path_loc).convert("RGB")
init_image_np = np.array(init_image)


# Open the image using PIL
torch_tensor = Image.open(path_loc)
print("Type after opening with PIL:", type(
    torch_tensor))  # <class 'PIL.Image.Image'>

# # Convert the PIL image to a NumPy array
# torch_tensor = np.array(pil_image)
# print("Type after converting to NumPy array:", type(
#     torch_tensor), torch_tensor.shape)  # <class 'numpy.ndarray'>

# # Convert the NumPy array to a PyTorch tensor
# torch_tensor = torch.from_numpy(np_image)
# print("Type after converting to PyTorch tensor:", type(
#     torch_tensor), torch_tensor.shape)  # <class 'torch.Tensor'>






# Define your prompt
prompt = "A futuristic cityscape at sunset with vibrant neon lights"

# Generate the new image
result = pipe(prompt=prompt, init_image=torch_tensor).images[0]

# Save and display the resulting image
result.save("img2img_result.png")
result.show()
