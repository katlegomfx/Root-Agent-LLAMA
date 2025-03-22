import tkinter as tk
import threading
import pygame
import sys
import io
import contextlib
from simple.code.tool_registry import tool_registry

# Global variables
desired_position = None  # Will be a tuple (x, y)
mode = "normal"  # Modes: "normal", "tool_selection", "python_code"
tk_root = None  # Will store the Tkinter root reference
# Name of the currently selected tool (in tool_selection mode)
selected_tool = None
tool_info_shown = False  # Flag to indicate whether tool info has been shown

DEFAULT_CODE = """def hello_world():
    print("Hello, World!")

hello_world()
"""


def get_tool_position(index, total):
    """Compute an (x, y) position for a tool given its index and total count.
    Tools are evenly spaced horizontally between x=50 and x=590 at y=150.
    """
    if total > 1:
        step = (640 - 100) / (total - 1)
    else:
        step = 0
    x = 50 + index * step
    y = 150
    return (int(x), int(y))


def launch_game():
    # Disable new game launch if already running.
    launch_button.config(state=tk.DISABLED)
    # Start the Pygame game in a separate thread so that Tkinter remains responsive.
    game_thread = threading.Thread(target=run_game, daemon=True)
    game_thread.start()


def run_game():
    global desired_position, mode, selected_tool, tool_info_shown
    # Initialize Pygame and create a window.
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Pygame Launched from Tkinter")
    clock = pygame.time.Clock()

    # Load images for targets.
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

    # Create a font for labels.
    font = pygame.font.SysFont("Arial", 20)

    # Starting position for the red agent square.
    agent_x = 300
    agent_y = 400

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Animate agent movement if a desired position is set.
        if desired_position is not None:
            target_x, target_y = desired_position
            if agent_x < target_x:
                agent_x = min(agent_x + 5, target_x)
            elif agent_x > target_x:
                agent_x = max(agent_x - 5, target_x)
            if agent_y < target_y:
                agent_y = min(agent_y + 5, target_y)
            elif agent_y > target_y:
                agent_y = max(agent_y - 5, target_y)
            if agent_x == target_x and agent_y == target_y:
                desired_position = None

        screen.fill((0, 0, 0))

        if mode == "normal":
            # Draw the Python target.
            python_target_rect = pygame.Rect(50, 100, 50, 50)
            if python_image:
                screen.blit(
                    python_image, (python_target_rect.x, python_target_rect.y))
            else:
                pygame.draw.rect(
                    screen, (0, 0, 255), (python_target_rect.x, python_target_rect.y, 25, 50))
                pygame.draw.rect(
                    screen, (255, 255, 0), (python_target_rect.x + 25, python_target_rect.y, 25, 50))
            python_label = font.render("Python", True, (255, 255, 255))
            screen.blit(python_label, (python_target_rect.x + (50 - python_label.get_width()) // 2,
                                       python_target_rect.y - python_label.get_height() - 5))

            # Draw the Tool target.
            tool_target_rect = pygame.Rect(500, 100, 50, 50)
            if tool_image:
                screen.blit(
                    tool_image, (tool_target_rect.x, tool_target_rect.y))
            else:
                pygame.draw.rect(screen, (128, 128, 128), tool_target_rect)
            tool_label = font.render("Tool", True, (255, 255, 255))
            screen.blit(tool_label, (tool_target_rect.x + (50 - tool_label.get_width()) // 2,
                                     tool_target_rect.y - tool_label.get_height() - 5))

            # Mode switches.
            if (agent_x, agent_y) == (50, 100):
                mode = "python_code"
                tk_root.after(0, show_python_code_window)
            if (agent_x, agent_y) == (500, 100):
                mode = "tool_selection"
                selected_tool = None  # Clear any previous tool selection.
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
            # If a tool was selected and the agent has arrived, show its information.
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

        # Draw the red Agent square.
        agent_rect = pygame.Rect(agent_x, agent_y, 50, 50)
        pygame.draw.rect(screen, (255, 0, 0), agent_rect)
        agent_label = font.render("Agent", True, (255, 255, 255))
        screen.blit(agent_label, (agent_x + (50 - agent_label.get_width()) // 2,
                                  agent_y - agent_label.get_height() - 5))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


def show_python_code_window():
    """Show a Tkinter window with default Python code and an Execute option."""
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

    def execute_code():
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


def show_tool_info_window(tool_name):
    """Show a Tkinter window with information about the specified tool."""
    info_window = tk.Toplevel(tk_root)
    info_window.title(f"Tool Information - {tool_name}")
    info_text = tk.Text(info_window, height=10, width=50)
    info_text.pack(padx=10, pady=10)
    tool_func = tool_registry.get(tool_name)
    doc = tool_func.__doc__ if tool_func and tool_func.__doc__ else "No documentation available."
    info_text.insert(tk.END, doc)
    info_text.config(state=tk.DISABLED)
    close_button = tk.Button(info_window, text="Close",
                             command=lambda: info_window.destroy())
    close_button.pack(padx=10, pady=10)


def move_to_python():
    """Set the agent's target position to that of the Python target."""
    global desired_position, mode
    if mode == "normal":
        desired_position = (50, 100)


def move_to_tool():
    """Set the agent's target position to that of the Tool target."""
    global desired_position, mode
    if mode == "normal":
        desired_position = (500, 100)


def return_to_start():
    """Return the agent to the starting position in normal mode."""
    global desired_position, mode
    if mode == "normal":
        desired_position = (300, 400)


def move_to_tool_dynamic(tool_name):
    """Set the agent's target position based on the dynamic tool's position."""
    global desired_position, mode, selected_tool, tool_info_shown
    if mode == "tool_selection":
        tools = list(tool_registry.keys())
        if tool_name in tools:
            index = tools.index(tool_name)
            pos = get_tool_position(index, len(tools))
            desired_position = pos
            selected_tool = tool_name
            tool_info_shown = False


def return_to_normal():
    """Exit tool selection (or python code) mode and return the agent to the starting position."""
    global mode, desired_position
    if mode in ("tool_selection", "python_code"):
        mode = "normal"
        desired_position = (300, 400)


# Create the Tkinter window.
root = tk.Tk()
root.title("Tkinter Launch Pygame")
tk_root = root  # Set the global tk_root reference

# Normal mode buttons.
launch_button = tk.Button(root, text="Launch Pygame Game", command=launch_game)
launch_button.pack(padx=20, pady=5)

python_button = tk.Button(root, text="Move to Python", command=move_to_python)
python_button.pack(padx=20, pady=5)

tool_button = tk.Button(root, text="Move to Tool", command=move_to_tool)
tool_button.pack(padx=20, pady=5)

return_button = tk.Button(
    root, text="Return to Start", command=return_to_start)
return_button.pack(padx=20, pady=5)

# Dynamically generate tool selection mode buttons.
tool_frame = tk.Frame(root)
tool_frame.pack(padx=20, pady=5)
for tool_name in tool_registry.keys():
    btn = tk.Button(tool_frame, text=f"Move to {tool_name}",
                    command=lambda tn=tool_name: move_to_tool_dynamic(tn))
    btn.pack(side=tk.LEFT, padx=5, pady=5)

return_normal_button = tk.Button(
    root, text="Return to Normal", command=return_to_normal)
return_normal_button.pack(padx=20, pady=5)

root.mainloop()
