from diffusers import StableDiffusionPipeline # type: ignore
import torch # type: ignore

# Load the Stable Diffusion pipeline (v1.5 in this case)
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", 
    # torch_dtype=torch.float16
)
# pipe = pipe.to("cpu")  # Use GPU for faster inference; remove or use "cpu" if needed

# Define your text prompt
prompt = "A futuristic cityscape with neon lights at night"

# Generate an image from the prompt
image = pipe(prompt).images[0]

# Save or display the image
image.save("generated_image.png")
image.show()
