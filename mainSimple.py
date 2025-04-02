from simple.code.gui.app import main
import os
import threading
from simple.image.imgen import generate_image  # Adjust import as needed


def generate_images_background():

    os.makedirs('simple/gag/', exist_ok=True)
    # Generate the Python logo for pygame with a transparent background.
    path = "simple/gag/pygame_python_logo.png"
    if not os.path.exists(path):
        generate_image(
            prompt="Python Programming Language logo",
            output_filename=path,
            transparent=True
        )
    # Generate the toolbox icon for pygame with a transparent background.
    path = "simple/gag/pygame_toolbox.png"
    if not os.path.exists(path):
        generate_image(
            prompt="Modern toolbox icon",
            output_filename=path,
            transparent=True
        )
    from simple.code.system_prompts import thesysname
    path = "simple/gag/icon.png"
    if not os.path.exists(path):
        generate_image(
            prompt=f"Robot Icon for a system called {thesysname}",
            output_filename=path,
            transparent=True
        )

    path = "simple/gag/avatar.png"
    if not os.path.exists(path):
        generate_image(
            prompt=f"Robot body of {thesysname}",
            output_filename=path,
            transparent=True
        )


# Start background thread before launching your main application.
generate_images_background()


if __name__ == '__main__':
    main()
