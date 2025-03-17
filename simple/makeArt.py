import matplotlib.pyplot as plt
import numpy as np
import os
import logging
from typing import List
from simple.code.utils import colored_print, strip_model_escapes, Fore
from simple.code.logging_config import setup_logging

# Centralized logging setup
setup_logging()


def create_artistic_png(data: List[float], filename: str = "gag/artistic_plot.png", style: str = "seaborn-darkgrid") -> None:
    """
    Creates an artistic PNG image from the provided data using a specified style.

    Enhancements:
    - Uses a custom style if available.
    - Colors data points using a colormap.
    - Combines scatter and line plots.
    - Adds annotations for each data point.

    Args:
        data (List[float]): List of numeric values to plot.
        filename (str, optional): Output file path for the PNG image.
        style (str, optional): Matplotlib style to use.
    """
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Created directory {output_dir} for output image.")

    available_styles = plt.style.available
    if style in available_styles:
        plt.style.use(style)
    else:
        logging.warning(
            f"Style '{style}' is not available. Using default style instead.")

    fig, ax = plt.subplots(figsize=(10, 8))
    x = np.arange(len(data))
    scatter = ax.scatter(x, data, c=data, cmap='viridis',
                         s=120, alpha=0.8, edgecolor='black')
    ax.plot(x, data, color='white', linewidth=2, linestyle='--')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Data Value', rotation=270, labelpad=15)
    ax.set_title("Artistic Data Plot", fontsize=20,
                 fontweight='bold', color='navy')
    ax.set_xlabel("Index", fontsize=14)
    ax.set_ylabel("Value", fontsize=14)

    for i, value in enumerate(data):
        ax.annotate(f'{value}', xy=(i, value), xytext=(5, 5),
                    textcoords='offset points', fontsize=10, color='darkred')

    try:
        plt.savefig(filename, format="png", dpi=300, bbox_inches='tight')
        logging.info(f"Artistic PNG image saved as '{filename}'.")
    except Exception as e:
        logging.error(f"Failed to save image {filename}: {e}")
    finally:
        plt.close()


if __name__ == "__main__":
    example_data = [1, 3, 2, 5, 7, 8, 6]
    create_artistic_png(example_data)
    colored_print(
        "Artistic PNG image created as 'gag/artistic_plot.png'.", Fore.BLUE)
