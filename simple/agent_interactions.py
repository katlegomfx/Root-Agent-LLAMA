"""
Refactored Agent Interactions Module

This module runs a Tkinter+Pygame simulation where the agent moves
to different target positions (Python code window, tool selection, etc.)
and then triggers the corresponding window.
"""

import tkinter as tk
import threading
import traceback
import pygame # type: ignore
import io
import contextlib
import queue  # Import queue for safer cross-thread communication
from typing import Optional, Tuple
from simple.code.tool_registry import tool_registry

DEFAULT_CODE = """def hello_world():
    print("Hello, World!")

hello_world()
"""

AGENT_SPEED = 5
WINDOW_SIZE = (640, 480)


class AgentInteractionManager:
    def __init__(self):
        self.desired_position: Optional[Tuple[int, int]] = None
        self.mode: str = "normal"  # Modes: "normal", "tool_selection", "python_code"
        self.tk_root: Optional[tk.Tk] = None
        self.selected_tool: Optional[str] = None
        self.tool_info_shown: bool = False
        self.status_msg: str = ""
        self.generated_python_code: str = ""
        self._pygame_running = threading.Event()  # Event to signal pygame loop state
        self._tk_queue = queue.Queue()  # Queue for Tkinter updates from Pygame thread


    def _ensure_tk_root(self):
        """Ensures tk_root exists, creating a hidden one if necessary."""
        if self.tk_root is None:
            print("Creating internal hidden Tk root.")
            self.tk_root = tk.Tk()
            self.tk_root.withdraw()  # Keep it hidden unless managed externally

    def _schedule_tk_update(self, callable_func, *args):
        """Safely schedule a function call in the Tkinter main thread."""
        self._ensure_tk_root()
        self._tk_queue.put((callable_func, args))
        if self.tk_root:
            self.tk_root.after(10, self._process_tk_queue)

    def _process_tk_queue(self):
        """Process pending updates from the queue in the Tkinter thread."""
        try:
            while not self._tk_queue.empty():
                callable_func, args = self._tk_queue.get_nowait()
                callable_func(*args)
        except queue.Empty:
            pass  # No more items for now
        except Exception as e:
            print(f"Error processing Tkinter queue item: {e}")

    def get_tool_position(self, index: int, total: int) -> Tuple[int, int]:
        """Compute evenly spaced positions for tools."""
        x_start, x_end = 50, 590
        step = (x_end - x_start) / (total - 1) if total > 1 else 0
        x = int(x_start + index * step)
        y = 150
        return x, y

    def update_status_msg(self, msg: str) -> None:
        self.status_msg = msg

    def set_generated_code(self, code: str) -> None:
        self.generated_python_code = code

    def launch_game(self) -> None:
        """Launches the Pygame simulation in a separate thread."""
        if not self._pygame_running.is_set():
            try:
                if hasattr(self, 'launch_button') and self.launch_button:
                    self.launch_button.config(state=tk.DISABLED)
            except (AttributeError, tk.TclError):
                pass
            self._pygame_running.set()  # Signal that pygame is starting/running
            game_thread = threading.Thread(target=self.run_game, daemon=True)
            game_thread.start()
        else:
            print("Pygame simulation is already running.")

    def stop_game(self):
        """Signals the Pygame loop to stop."""
        self._pygame_running.clear()  # Signal pygame to stop
        print("Attempting to stop Pygame simulation...")

    def run_game(self) -> None:
        """Runs the main Pygame simulation loop."""
        try:
            pygame.init()
            screen = pygame.display.set_mode(WINDOW_SIZE)
            pygame.display.set_caption("Agent Interaction Simulation")
            self._set_pygame_icon()
            clock = pygame.time.Clock()
            python_image = self._load_image(
                "simple/gag/pygame_python_logo.png", (50, 50))
            tool_image = self._load_image(
                "simple/gag/pygame_toolbox.png", (50, 50))
            font = pygame.font.SysFont("Arial", 20)
            agent_x, agent_y = 300, 400

            while self._pygame_running.is_set():  # Check the event flag
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.stop_game()  # Use the stop method
                        break  # Exit inner loop

                if not self._pygame_running.is_set():  # Check again after event processing
                    break

                agent_x, agent_y = self._move_agent(agent_x, agent_y)
                screen.fill((0, 0, 0))

                if self.mode == "normal":
                    self._render_normal_mode(
                        screen, font, python_image, tool_image, agent_x, agent_y)
                elif self.mode == "tool_selection":
                    self._render_tool_selection(screen, font, agent_x, agent_y)
                elif self.mode == "python_code":
                    self._render_python_code(screen, font)

                self._draw_agent(screen, font, agent_x, agent_y)

                if self.status_msg:
                    status_surface = font.render(
                        self.status_msg, True, (255, 255, 255))
                    screen.blit(status_surface, (50, 450))

                pygame.display.flip()
                clock.tick(30)

        except pygame.error as e:
            print(f"Pygame error occurred: {e}")
            self._pygame_running.clear()  # Ensure flag is cleared on error
        finally:
            pygame.quit()
            print("Pygame quit.")
            try:
                if hasattr(self, 'launch_button') and self.launch_button and self.tk_root:
                    self._schedule_tk_update(lambda btn: btn.config(
                        state=tk.NORMAL), self.launch_button)
            except tk.TclError:
                pass

    def _set_pygame_icon(self):
        try:
            icon_path = "simple/gag/icon.png"
            icon_image = pygame.image.load(icon_path).convert_alpha()
            icon_image = pygame.transform.scale(icon_image, (32, 32))
            pygame.display.set_icon(icon_image)
        except Exception as e:
            print(f"Error loading pygame icon '{icon_path}': {e}")

    def _load_image(self, path: str, size: Tuple[int, int]) -> Optional[pygame.Surface]:
        try:
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, size)
        except Exception as e:
            print(f"Error loading image '{path}': {e}")
            return None

    def _move_agent(self, agent_x: int, agent_y: int) -> Tuple[int, int]:
        if self.desired_position is None:
            return agent_x, agent_y

        target_x, target_y = self.desired_position
        dx = target_x - agent_x
        dy = target_y - agent_y

        if dx > 0:
            agent_x = min(agent_x + AGENT_SPEED, target_x)
        elif dx < 0:
            agent_x = max(agent_x - AGENT_SPEED, target_x)

        if dy > 0:
            agent_y = min(agent_y + AGENT_SPEED, target_y)
        elif dy < 0:
            agent_y = max(agent_y - AGENT_SPEED, target_y)

        if (agent_x, agent_y) == (target_x, target_y):
            self.desired_position = None  # Arrived

        return agent_x, agent_y

    def _render_normal_mode(self, screen, font, python_image, tool_image, agent_x, agent_y):
        python_target_pos = (50, 100)
        tool_target_pos = (500, 100)

        python_target_rect = pygame.Rect(*python_target_pos, 50, 50)
        if python_image:
            screen.blit(python_image, python_target_rect.topleft)
        else:  # Fallback rendering
            pygame.draw.rect(
                screen, (0, 0, 255), (python_target_rect.x, python_target_rect.y, 25, 50))
            pygame.draw.rect(
                screen, (255, 255, 0), (python_target_rect.x + 25, python_target_rect.y, 25, 50))
        python_label = font.render("Python", True, (255, 255, 255))
        screen.blit(python_label, (python_target_rect.centerx - python_label.get_width() // 2,
                                   python_target_rect.top - python_label.get_height() - 5))

        tool_target_rect = pygame.Rect(*tool_target_pos, 50, 50)
        if tool_image:
            screen.blit(tool_image, tool_target_rect.topleft)
        else:  # Fallback rendering
            pygame.draw.rect(screen, (128, 128, 128), tool_target_rect)
        tool_label = font.render("Tool", True, (255, 255, 255))
        screen.blit(tool_label, (tool_target_rect.centerx - tool_label.get_width() // 2,
                                 tool_target_rect.top - tool_label.get_height() - 5))

        if self.desired_position is None:  # Only trigger if not moving
            if (agent_x, agent_y) == python_target_pos:
                self.mode = "python_code"
                self._schedule_tk_update(self.show_python_code_window)
            elif (agent_x, agent_y) == tool_target_pos:
                self.mode = "tool_selection"
                self.selected_tool = None
                self.tool_info_shown = False

    def _render_tool_selection(self, screen, font, agent_x, agent_y):
        header = font.render("Tool Selection Mode", True, (255, 255, 255))
        screen.blit(header, (WINDOW_SIZE[0] //
                    2 - header.get_width() // 2, 20))

        tools = list(tool_registry.keys())
        total = len(tools)
        if total == 0:
            no_tools_label = font.render(
                "No tools registered", True, (255, 100, 100))
            screen.blit(
                no_tools_label, (WINDOW_SIZE[0] // 2 - no_tools_label.get_width() // 2, 100))
            return  # Nothing else to render

        for i, tool_name in enumerate(tools):
            pos = self.get_tool_position(i, total)
            rect = pygame.Rect(pos[0] - 25, pos[1] - 25, 50, 50)
            color = (100 + i * (155 // total) if total >
                     0 else 100, 100, 150)  # Adjust color spread
            pygame.draw.rect(screen, color, rect)
            label = font.render(tool_name, True, (255, 255, 255))
            screen.blit(
                label, (rect.centerx - label.get_width() // 2, rect.top - label.get_height() - 5))

            if self.desired_position is None and (agent_x, agent_y) == pos:
                if self.selected_tool == tool_name and not self.tool_info_shown:
                    self.tool_info_shown = True
                    self._schedule_tk_update(
                        self.show_tool_info_window, self.selected_tool)
                elif self.selected_tool != tool_name:
                    print(
                        f"Warning: Agent arrived at tool '{tool_name}' but expected '{self.selected_tool}'")

    def _render_python_code(self, screen, font):
        header = font.render("Python Code Mode", True, (255, 255, 255))
        screen.blit(header, (WINDOW_SIZE[0] //
                    2 - header.get_width() // 2, 20))
        if self.generated_python_code:
            lines = self.generated_python_code.splitlines()
            y_offset = 60
            max_lines = (WINDOW_SIZE[1] - y_offset - 50) // font.get_linesize()  # Limit lines shown
            for i, line in enumerate(lines):
                if i >= max_lines:
                    more_lines_surf = font.render("...", True, (200, 200, 200))
                    screen.blit(more_lines_surf, (50, y_offset))
                    break
                code_surface = font.render(line, True, (200, 200, 200))
                screen.blit(code_surface, (50, y_offset))
                y_offset += font.get_linesize()
        else:
            prompt = font.render(
                "Executing default code...", True, (255, 255, 255))
            screen.blit(
                prompt, (WINDOW_SIZE[0] // 2 - prompt.get_width() // 2, 60))

    def _draw_agent(self, screen, font, agent_x, agent_y):
        agent_rect = pygame.Rect(agent_x - 25, agent_y - 25, 50, 50)
        pygame.draw.rect(screen, (255, 0, 0), agent_rect)
        agent_label = font.render("Agent", True, (255, 255, 255))
        screen.blit(agent_label, (agent_rect.centerx - agent_label.get_width() // 2,
                                  agent_rect.top - agent_label.get_height() - 5))

    def _close_code_window_and_return(self, window: tk.Toplevel):
        """Helper to close the code window and trigger return."""
        try:
            window.destroy()
        except tk.TclError:
            pass  # Window might already be closed
        self.return_to_normal()

    def show_python_code_window(self) -> None:
        self._ensure_tk_root()
        code_window = tk.Toplevel(self.tk_root)
        code_window.title("Python Code Execution")
        code_window.transient(self.tk_root)  # Associate with main window
        code_window.grab_set()  # Make modal

        code_to_run = self.generated_python_code if self.generated_python_code else DEFAULT_CODE
        code_title = "Generated Python Code" if self.generated_python_code else "Default Python Code"

        title_label = tk.Label(
            code_window, text=code_title, font=("Arial", 12, "bold"))
        title_label.pack(padx=10, pady=(10, 5))

        code_text = tk.Text(code_window, height=10, width=60)
        code_text.pack(padx=10, pady=5)
        code_text.insert(tk.END, code_to_run)
        code_text.config(state=tk.DISABLED)

        output_label = tk.Label(code_window, text="Output:")
        output_label.pack(padx=10, pady=(10, 0))
        output_text = tk.Text(code_window, height=5, width=60)
        output_text.pack(padx=10, pady=5)
        output_text.insert(tk.END, "Click 'Execute' to run...")
        output_text.config(state=tk.DISABLED)

        execution_done = threading.Event()

        def execute_code_action() -> None:
            if execution_done.is_set():
                return  # Already executed or executing

            execution_done.set()
            execute_button.config(state=tk.DISABLED)  # Disable button during execution
            output_text.config(state=tk.NORMAL)
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, "Executing...")
            output_text.config(state=tk.DISABLED)
            code_window.update_idletasks()  # Ensure "Executing..." is shown

            f = io.StringIO()
            try:
                with contextlib.redirect_stdout(f):
                    exec(code_to_run)
                output = f.getvalue()
                if not output:
                    output = "[No output produced]"
            except Exception as e:
                output = f"Error during execution:\n{e}\n{traceback.format_exc()}"
            finally:
                f.close()

            output_text.config(state=tk.NORMAL)
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, output)
            output_text.config(state=tk.DISABLED)

            code_window.after(
                3000, self._close_code_window_and_return, code_window)

        execute_button = tk.Button(
            code_window, text="Execute Code", command=execute_code_action)
        execute_button.pack(padx=10, pady=10)

        code_window.after(100, execute_code_action)

    def show_tool_info_window(self, tool_name: str) -> None:
        self._ensure_tk_root()
        info_window = tk.Toplevel(self.tk_root)
        info_window.title(f"Tool Information - {tool_name}")
        info_window.transient(self.tk_root)  # Associate with main window
        info_window.grab_set()  # Make modal

        info_text = tk.Text(info_window, height=10, width=60, wrap=tk.WORD)
        info_text.pack(padx=10, pady=10)

        tool_func = tool_registry.get(tool_name)
        doc = "Documentation not available."
        if tool_func:
            doc = tool_func.__doc__ if tool_func.__doc__ else "No documentation provided."

        info_text.insert(tk.END, doc.strip())
        info_text.config(state=tk.DISABLED)

        def close_and_return():
            try:
                info_window.destroy()
            except tk.TclError:
                pass  # Window might already be closed

        close_button = tk.Button(
            info_window, text="Close", command=close_and_return)
        close_button.pack(padx=10, pady=10)

        info_window.after(4000, close_and_return)
        info_window.after(4100, self.return_to_normal)  # Schedule return slightly after close

    def move_to_python(self) -> None:
        if self.mode == "normal":
            self.desired_position = (50, 100)  # Target position for Python
            print("Agent moving to Python interaction point.")

    def move_to_tool(self) -> None:
        if self.mode == "normal":
            self.desired_position = (500, 100)  # Target position for Tool Selection entry
            print("Agent moving to Tool interaction point.")

    def return_to_start(self) -> None:
        if self.mode == "normal":
            self.desired_position = (300, 400)  # Center start position
            print("Agent returning to start position.")

    def move_to_tool_dynamic(self, tool_name: str) -> None:
        if self.mode == "tool_selection":
            try:
                tools = list(tool_registry.keys())
                if tool_name in tools:
                    index = tools.index(tool_name)
                    pos = self.get_tool_position(index, len(tools))
                    self.desired_position = pos  # Target position for the specific tool
                    self.selected_tool = tool_name
                    self.tool_info_shown = False  # Reset flag for showing info window
                    print(f"Agent moving to tool: {tool_name}")
                else:
                    print(
                        f"Warning: Tool '{tool_name}' not found in registry for movement.")
            except ValueError:
                print(f"Error: Tool '{tool_name}' not found while trying to move.")
        else:
            print(f"Warning: Cannot move to tool '{tool_name}' from mode '{self.mode}'.")

    def return_to_normal(self) -> None:
        """Sets mode to normal and moves agent towards the start position."""
        if self.mode in ("tool_selection", "python_code"):
            print(f"Returning to normal mode from {self.mode}.")
            self.mode = "normal"
            self.selected_tool = None
            self.tool_info_shown = False
            self.generated_python_code = ""  # Clear generated code display
            self.desired_position = (300, 400)  # Center start position
        elif self.mode == "normal" and self.desired_position is None:
            self.desired_position = (300, 400)

    def launch_agent_interaction(self) -> None:
        """Public method to launch the game, ensuring Tk root is available."""
        self._ensure_tk_root()  # Make sure Tkinter is initialized
        self.launch_game()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Agent Interaction Test Controller")
    manager = AgentInteractionManager()
    manager.tk_root = root  # Use the main Tkinter window for this test setup

    manager.launch_button = tk.Button(
        root, text="Launch Agent Simulation", command=manager.launch_agent_interaction)
    manager.launch_button.pack(padx=20, pady=20)

    control_frame = tk.Frame(root)
    control_frame.pack(padx=20, pady=10)

    tk.Label(control_frame, text="Manual Agent Control:").pack()

    python_choice = tk.Button(
        control_frame, text="Move to Python", command=manager.move_to_python)
    python_choice.pack(side=tk.LEFT, padx=5)

    tool_choice = tk.Button(control_frame, text="Move to Tool Select",
                            command=manager.move_to_tool)
    tool_choice.pack(side=tk.LEFT, padx=5)

    tool_names = list(tool_registry.keys())
    if tool_names:
        dynamic_tool_frame = tk.Frame(root)
        dynamic_tool_frame.pack(padx=20, pady=10)
        tk.Label(dynamic_tool_frame,
                 text="Move to Specific Tool (requires Tool Select mode):").pack()
        for name in tool_names[:3]:  # Show first few tools as example
            btn = tk.Button(dynamic_tool_frame, text=f"Move to {name}",
                             command=lambda n=name: manager.move_to_tool_dynamic(n))
            btn.pack(side=tk.LEFT, padx=5)

    return_normal_button = tk.Button(
        control_frame, text="Return to Normal/Start", command=manager.return_to_normal)
    return_normal_button.pack(side=tk.LEFT, padx=5)

    def on_closing():
        print("Controller window closing...")
        manager.stop_game()  # Signal pygame to stop if running
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
