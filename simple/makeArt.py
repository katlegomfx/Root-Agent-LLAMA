import matplotlib.pyplot as plt
import numpy as np
import os
from typing import List


def create_artistic_png(data: List[float], filename: str = "gag/artistic_plot.png", style: str = "seaborn-darkgrid") -> None:
    """
    Creates an artistic PNG image from the provided data using a specified style.

    If the given style is not available, it will use the default style instead.

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
    # Ensure the output directory exists.
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    available_styles = plt.style.available
    if style in available_styles:
        plt.style.use(style)
    else:
        print(
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

    plt.savefig(filename, format="png", dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    example_data = [1, 3, 2, 5, 7, 8, 6]
    create_artistic_png(example_data)
    print("Artistic PNG image created as 'gag/artistic_plot.png'.")
