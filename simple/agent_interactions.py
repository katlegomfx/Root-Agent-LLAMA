"""
Agent Interactions Module

This module runs a Tkinter+Pygame simulation where the agent moves
to different target positions (Python code window, tool selection, etc.)
and then triggers the corresponding window.
"""

import tkinter as tk
import threading
import pygame # type: ignore
import sys
import io
import contextlib
from simple.code.tool_registry import tool_registry
from typing import Optional, Tuple

# Global state variables with type annotations
desired_position: Optional[Tuple[int, int]] = None  # Tuple (x, y)
mode: str = "normal"  # Modes: "normal", "tool_selection", "python_code"
tk_root: Optional[tk.Tk] = None  # Tkinter root reference
# Currently selected tool (in tool_selection mode)
selected_tool: Optional[str] = None
tool_info_shown: bool = False  # Whether tool info has been shown
status_msg: str = ""  # Global status message shown in pygame

DEFAULT_CODE: str = """def hello_world():
    print("Hello, World!")

hello_world()
"""

AGENT_SPEED: int = 5
WINDOW_SIZE: Tuple[int, int] = (640, 480)


def get_tool_position(index: int, total: int) -> Tuple[int, int]:
    """Compute an (x, y) position for a tool given its index and total count.
    Tools are evenly spaced horizontally between x=50 and x=590 at y=150.
    """
    x_start, x_end = 50, 590
    if total > 1:
        step = (x_end - x_start) / (total - 1)
    else:
        step = 0
    x = x_start + index * step
    y = 150
    return int(x), int(y)


def update_status_msg(msg: str) -> None:
    """Update the global status message that is drawn on the pygame screen."""
    global status_msg
    status_msg = msg


def launch_game() -> None:
    """Launch the agent interaction game (Pygame simulation)."""
    try:
        launch_button.config(state=tk.DISABLED)
    except NameError:
        pass
    game_thread = threading.Thread(target=run_game, daemon=True)
    game_thread.start()


def run_game() -> None:
    global desired_position, mode, selected_tool, tool_info_shown, status_msg, tk_root

    if tk_root is None:
        temp_root = tk.Tk()
        temp_root.withdraw()
        tk_root = temp_root

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Agent Interaction Simulation")

    # Set pygame window icon to match the Tkinter icon
    try:
        icon_path = "gag/artistic_plot.png"
        icon_image = pygame.image.load(icon_path).convert_alpha()
        # Optionally, scale the icon to a suitable size (e.g., 32x32)
        icon_image = pygame.transform.scale(icon_image, (32, 32))
        pygame.display.set_icon(icon_image)
    except Exception as e:
        print("Error loading pygame icon:", e)

    clock = pygame.time.Clock()

    try:
        python_image = pygame.image.load("python_logo.png").convert_alpha()
        python_image = pygame.transform.scale(python_image, (50, 50))
    except Exception as e:
        print("Error loading python_logo.png:", e)
        python_image = None

    try:
        tool_image = pygame.image.load("tool_box.png").convert_alpha()
        tool_image = pygame.transform.scale(tool_image, (50, 50))
    except Exception as e:
        print("Error loading tool_box.png:", e)
        tool_image = None

    font = pygame.font.SysFont("Arial", 20)
    agent_x, agent_y = 300, 400

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Move agent toward desired position if set
        if desired_position is not None:
            target_x, target_y = desired_position
            if agent_x < target_x:
                agent_x = min(agent_x + AGENT_SPEED, target_x)
            elif agent_x > target_x:
                agent_x = max(agent_x - AGENT_SPEED, target_x)
            if agent_y < target_y:
                agent_y = min(agent_y + AGENT_SPEED, target_y)
            elif agent_y > target_y:
                agent_y = max(agent_y - AGENT_SPEED, target_y)
            if (agent_x, agent_y) == (target_x, target_y):
                desired_position = None

        screen.fill((0, 0, 0))
        if mode == "normal":
            # Render Python button
            python_target_rect = pygame.Rect(50, 100, 50, 50)
            if python_image:
                screen.blit(python_image, python_target_rect.topleft)
            else:
                pygame.draw.rect(
                    screen, (0, 0, 255), (python_target_rect.x, python_target_rect.y, 25, 50))
                pygame.draw.rect(
                    screen, (255, 255, 0), (python_target_rect.x + 25, python_target_rect.y, 25, 50))
            python_label = font.render("Python", True, (255, 255, 255))
            screen.blit(python_label, (python_target_rect.x + (50 - python_label.get_width()) // 2,
                                       python_target_rect.y - python_label.get_height() - 5))
            # Render Tool button
            tool_target_rect = pygame.Rect(500, 100, 50, 50)
            if tool_image:
                screen.blit(tool_image, tool_target_rect.topleft)
            else:
                pygame.draw.rect(screen, (128, 128, 128), tool_target_rect)
            tool_label = font.render("Tool", True, (255, 255, 255))
            screen.blit(tool_label, (tool_target_rect.x + (50 - tool_label.get_width()) // 2,
                                     tool_target_rect.y - tool_label.get_height() - 5))
            # Trigger mode transitions based on agent location
            if (agent_x, agent_y) == (50, 100):
                mode = "python_code"
                tk_root.after(0, show_python_code_window)
            if (agent_x, agent_y) == (500, 100):
                mode = "tool_selection"
                selected_tool = None
                tool_info_shown = False

        elif mode == "tool_selection":
            header = font.render("Tool Selection Mode", True, (255, 255, 255))
            screen.blit(header, (200, 20))
            tools = list(tool_registry.keys())
            total = len(tools)
            tool_positions = [get_tool_position(
                i, total) for i in range(total)]
            for i, tool_name in enumerate(tools):
                pos = tool_positions[i]
                rect = pygame.Rect(pos[0], pos[1], 50, 50)
                color = (100 + i * 50, 100, 150)
                pygame.draw.rect(screen, color, rect)
                label = font.render(tool_name, True, (255, 255, 255))
                screen.blit(
                    label, (pos[0] + (50 - label.get_width()) // 2, pos[1] - label.get_height() - 5))
            # Show tool information when the agent reaches the selected tool
            if selected_tool is not None and desired_position is None and not tool_info_shown:
                tools = list(tool_registry.keys())
                index = tools.index(selected_tool)
                pos = get_tool_position(index, len(tools))
                if (agent_x, agent_y) == pos:
                    tool_info_shown = True
                    tk_root.after(0, show_tool_info_window, selected_tool)

        elif mode == "python_code":
            header = font.render("Python Code Mode", True, (255, 255, 255))
            screen.blit(header, (220, 20))
            prompt = font.render(
                "Executing default code...", True, (255, 255, 255))
            screen.blit(prompt, (200, 60))

        # Draw agent
        agent_rect = pygame.Rect(agent_x, agent_y, 50, 50)
        pygame.draw.rect(screen, (255, 0, 0), agent_rect)
        agent_label = font.render("Agent", True, (255, 255, 255))
        screen.blit(agent_label, (agent_x + (50 - agent_label.get_width()) // 2,
                                  agent_y - agent_label.get_height() - 5))

        # Draw status message at the bottom
        if status_msg:
            status_surface = font.render(
                str(status_msg), True, (255, 255, 255))
            screen.blit(status_surface, (50, 450))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


def show_python_code_window() -> None:
    """Creates a Tkinter window to show and execute the default Python code."""
    code_window = tk.Toplevel(tk_root)
    code_window.title("Default Python Code")
    code_text = tk.Text(code_window, height=10, width=50)
    code_text.pack(padx=10, pady=10)
    code_text.insert(tk.END, DEFAULT_CODE)
    code_text.config(state=tk.DISABLED)
    output_label = tk.Label(code_window, text="Output:")
    output_label.pack(padx=10, pady=(10, 0))
    output_text = tk.Text(code_window, height=5, width=50)
    output_text.pack(padx=10, pady=10)

    def execute_code() -> None:
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            try:
                exec(DEFAULT_CODE)
            except Exception as e:
                print("Error during execution:", e)
        output = f.getvalue()
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, output)
        code_window.after(
            3000, lambda: [code_window.destroy(), return_to_normal()])

    execute_button = tk.Button(
        code_window, text="Execute Code", command=execute_code)
    execute_button.pack(padx=10, pady=10)


def show_tool_info_window(tool_name: str) -> None:
    """Creates a Tkinter window to display documentation for the selected tool."""
    info_window = tk.Toplevel(tk_root)
    info_window.title(f"Tool Information - {tool_name}")
    info_text = tk.Text(info_window, height=10, width=50)
    info_text.pack(padx=10, pady=10)
    tool_func = tool_registry.get(tool_name)
    doc = tool_func.__doc__ if tool_func and tool_func.__doc__ else "No documentation available."
    info_text.insert(tk.END, doc)
    info_text.config(state=tk.DISABLED)
    close_button = tk.Button(info_window, text="Close",
                             command=info_window.destroy)
    close_button.pack(padx=10, pady=10)


def move_to_python() -> None:
    """Set target position to the Python button."""
    global desired_position, mode
    if mode == "normal":
        desired_position = (50, 100)


def move_to_tool() -> None:
    """Set target position to the Tool button."""
    global desired_position, mode
    if mode == "normal":
        desired_position = (500, 100)


def return_to_start() -> None:
    """Return the agent to the starting position."""
    global desired_position, mode
    if mode == "normal":
        desired_position = (300, 400)


def move_to_tool_dynamic(tool_name: str) -> None:
    """Move the agent to the position of a specific tool in tool-selection mode."""
    global desired_position, mode, selected_tool, tool_info_shown
    if mode == "tool_selection":
        tools = list(tool_registry.keys())
        if tool_name in tools:
            index = tools.index(tool_name)
            pos = get_tool_position(index, len(tools))
            desired_position = pos
            selected_tool = tool_name
            tool_info_shown = False


def return_to_normal() -> None:
    """Return the agent to normal mode and starting position."""
    global mode, desired_position
    if mode in ("tool_selection", "python_code"):
        mode = "normal"
        desired_position = (300, 400)


def launch_agent_interaction() -> None:
    """Exposed function to launch the agent interaction simulation."""
    launch_game()


if __name__ == "__main__":
    tk_root = tk.Tk()
    tk_root.title("Agent Interaction Test")
    launch_button = tk.Button(
        tk_root, text="Launch Agent Interaction", command=launch_agent_interaction)
    launch_button.pack(padx=20, pady=20)
    python_choice = tk.Button(
        tk_root, text="Choose Python", command=move_to_python)
    python_choice.pack(padx=20, pady=10)
    tool_choice = tk.Button(tk_root, text="Choose Tool", command=move_to_tool)
    tool_choice.pack(padx=20, pady=10)
    tk_root.mainloop()
