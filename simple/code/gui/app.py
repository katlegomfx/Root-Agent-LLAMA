# ./simple/code/gui/app.py:
#!/usr/bin/env python3
"""
GUI Application for Flexi💻AI

This module contains the Tkinter-based GUI for interacting with the agent.
It is completely separated from the agent’s core execution logic.
"""

import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import asyncio
import json
import logging
import random
import signal  # Import signal module
import sys  # Import sys module
from typing import Any, List, Dict, Tuple, Union

from simple.code import utils
from simple.code.inference import run_inference, current_client  # Import current_client
from simple.code.utils import code_corpus, colored_print, Fore
from simple.code.logging_config import setup_logging
from simple.code.agent_executor import AgentExecutor
from simple.code.system_prompts import MD_HEADING, load_message_template
# AgentInteractionManager is instantiated within AgentExecutor if not provided
from simple.agent_interactions import AgentInteractionManager

setup_logging()


def create_labeled_scrolled_text(parent: tk.Frame, label_text: str, height: int, bg_color: str) -> ScrolledText:
    """
    Helper function to create a label and a ScrolledText widget.
    """
    label = tk.Label(parent, text=label_text)
    label.pack(anchor="w")
    text_area = ScrolledText(parent, height=height, bg=bg_color)
    text_area.pack(fill=tk.BOTH, expand=True, pady=5)
    return text_area


class FlexiAgentApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Flexi💻AI")
        self.set_app_icon()
        self.summary = ""
        self.text_history = []
        self.history_index = None
        self.model_var = tk.StringVar(value="llama3.2")  # Default model
        self.full_prompt = ""
        self.auto_prompt_set = False
        self.first_check = False

        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        self.conversation_history_enabled = tk.BooleanVar(value=True)
        self.conversation_turns = 3  # Turns before summarizing

        # Instantiate the AgentExecutor and its AgentInteractionManager
        # If you want the GUI to manage the Tk root for the simulation, pass it here
        self.agent_manager = AgentInteractionManager()
        self.agent_manager.tk_root = self.root  # Let the manager use the main Tk root
        self.agent_executor = AgentExecutor(
            model_name=self.model_var.get(),
            agent_manager=self.agent_manager
        )
        # Also assign the model_var to agent_executor for updates (if needed, though decide_execution already reads it)
        self.agent_executor.model_var = self.model_var

        self.build_gui()
        # Bind the up key for input history
        self.input_text_area.bind("<Up>", self.on_up_key)
        # Bind the window close button to the on_closing method
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Start the input check loop
        self.check_input()

    def build_gui(self) -> None:
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Right frame: Interaction and Action Output areas
        right_frame = tk.Frame(frame, bg="lightgray")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH,
                         expand=True, padx=(10, 0), pady=(0, 5))

        tk.Label(right_frame, text="Interaction Output", bg="lightgray", font=(
            "Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=(0, 2))
        self.interaction_output_area = ScrolledText(
            right_frame, state=tk.DISABLED, bg="white", width=40, height=10)  # Adjusted height
        self.interaction_output_area.grid(
            row=1, column=0, padx=5, pady=5, sticky="nsew")

        tk.Label(right_frame, text="Action Output", bg="lightgray", font=(
            "Helvetica", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=(10, 2))
        self.action_output_area = ScrolledText(
            right_frame, state=tk.DISABLED, bg="white", width=40, height=10)  # Adjusted height
        self.action_output_area.grid(
            row=3, column=0, padx=5, pady=5, sticky="nsew")

        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_rowconfigure(3, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Left frame: Input, Output, Scratchpad, and History
        left_frame = tk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH,
                        expand=True, padx=(0, 5), pady=(0, 5))

        # Configuration Panel (Model, Directory, Tips)
        config_panel = tk.Frame(left_frame, bd=1, relief=tk.SUNKEN)
        config_panel.pack(fill=tk.X, pady=(0, 10))
        self.build_config_panel(config_panel)

        # Input Area
        self.build_input_area(left_frame)

        # Output Area
        self.build_output_area(left_frame)

        # Scratchpad Area
        self.build_scratchpad_area(left_frame)

        # History Area
        history_panel = tk.Frame(left_frame)
        history_panel.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.build_history_area(history_panel)
        self.build_conversation_history_toggle(history_panel)

    def build_config_panel(self, parent: tk.Frame) -> None:
        """Builds the top configuration panel."""
        tk.Label(parent, text="Model:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        # TODO: Populate dropdown with available models dynamically if possible
        model_options = ["llama3.1", "llama3",
            "codellama", "mistral"]  # Example models
        self.model_dropdown = tk.OptionMenu(
            parent, self.model_var, *model_options)
        self.model_dropdown.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        tk.Label(parent, text="Work Dir:").grid(
            row=1, column=0, sticky="w", padx=5, pady=2)
        self.codebase_path_entry = tk.Entry(parent)
        self.codebase_path_entry.grid(
            row=1, column=1, padx=5, pady=2, sticky="ew")
        # TODO: Add browse button?

        tk.Label(parent, text="Tips:").grid(
            row=2, column=0, sticky="nw", padx=5, pady=2)
        self.tips_entry = tk.Text(parent, height=2)  # Reduced height
        self.tips_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        parent.grid_columnconfigure(1, weight=1)

    def build_input_area(self, parent: tk.Frame) -> None:
        input_frame = tk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(0, 5))  # Changed pack options
        tk.Label(input_frame, text="Enter your request:").pack(anchor="w")
        self.input_text_area = tk.Text(
            input_frame, height=4)  # Adjusted height
        self.input_text_area.pack(fill=tk.X, expand=True)
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        self.submit_button = tk.Button(
            button_frame, text="Submit", command=self.submit_text)
        self.submit_button.pack(side=tk.LEFT, padx=(0, 5))
        self.cancel_button = tk.Button(
            button_frame, text="Cancel", command=self.cancel_inference)
        self.cancel_button.pack(side=tk.LEFT)
        # Add simulation button if manager exists
        if self.agent_manager:
            self.simulation_button = tk.Button(
                button_frame, text="Show Simulation", command=self.agent_manager.launch_agent_interaction)
            self.simulation_button.pack(side=tk.RIGHT)
            # Link button to manager instance for enabling/disabling
            self.agent_manager.launch_button = self.simulation_button

    def build_output_area(self, parent: tk.Frame) -> None:
        output_frame = tk.Frame(parent)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.output_text_area = create_labeled_scrolled_text(
            output_frame, "Output:", 8, "lightyellow")  # Adjusted height

    def build_scratchpad_area(self, parent: tk.Frame) -> None:
        scratchpad_frame = tk.Frame(parent)
        scratchpad_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.agent_scratchpad_text_area = create_labeled_scrolled_text(
            scratchpad_frame, "Scratchpad:", 8, "lightgray")  # Adjusted height

    def build_history_area(self, parent: tk.Frame) -> None:
        # history_frame = tk.Frame(parent)
        # history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.user_history = create_labeled_scrolled_text(
            parent, "User Input History:", 5, "lightblue")  # Adjusted height
        self.user_history.config(state=tk.DISABLED)

    def build_conversation_history_toggle(self, parent: tk.Frame) -> None:
        toggle_frame = tk.Frame(parent)
        # Place at bottom of history panel
        toggle_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        self.history_checkbutton = tk.Checkbutton(
            toggle_frame, text="Enable Conversation History (Memory)", variable=self.conversation_history_enabled)
        self.history_checkbutton.pack(side=tk.LEFT)

    def update_interaction_output(self, role: str, content: str) -> None:
        """Appends formatted text to the interaction output area."""
        if not self.root or not self.interaction_output_area.winfo_exists():
            return  # Avoid errors if window closed
        try:
            formatted_text = f"Role: {role}\nContent:\n{content}\n{'-'*40}\n"
            self.interaction_output_area.config(state=tk.NORMAL)
            self.interaction_output_area.insert(tk.END, formatted_text)
            self.interaction_output_area.see(tk.END)
            self.interaction_output_area.config(state=tk.DISABLED)
        except tk.TclError as e:
            logging.warning(
                f"Failed to update interaction output (window might be closing): {e}")

    def set_app_icon(self) -> None:
        """Sets the application icon."""
        icon_path = 'simple/gag/icon.png'  # Define icon path
        # Check if icon exists, create dummy if not (optional)
        if not os.path.exists(icon_path):
            logging.warning(
                f"Icon file not found at {icon_path}. Skipping icon setting.")
             # You could create a placeholder or use a default icon here if needed.
            return
        try:
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
            logging.info(f"Loaded application icon from {icon_path}")
        except tk.TclError as e:
            # This can happen if Tkinter imaging libs aren't fully available (e.g., for PNG)
            # or if the file is corrupted.
            logging.error(
                f"Failed to load application icon '{icon_path}': {e}. Is the image format supported?")
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while loading icon '{icon_path}': {e}")

    def run_async_in_thread(self, coroutine: Any, callback: Any) -> None:
        """Runs an asyncio coroutine in a separate thread and calls callback with result."""
        def worker() -> None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(coroutine)
            except Exception as e:
                logging.exception("Error in asynchronous coroutine")
                result = f"Error: {str(e)}"  # Pass error as result
            finally:
                loop.close()
                # Schedule callback in the main Tkinter thread
                if self.root.winfo_exists():  # Check if root window still exists
                    self.root.after(0, callback, result)

        threading.Thread(target=worker, daemon=True).start()

    def cancel_inference(self):
        """Cancels the ongoing inference if possible."""
        global current_client
        if current_client:
            logging.info("Attempting to cancel inference...")
            colored_print("Attempting to cancel inference...", Fore.YELLOW)
            current_client.cancel()
            # Re-enable submit button
            self.submit_button.config(state=tk.NORMAL)
        else:
            logging.info("No active inference client to cancel.")
            colored_print("No active inference to cancel.", Fore.YELLOW)

    def submit_text(self) -> None:
        """Handles the submission of user input."""
        user_input = self.input_text_area.get("1.0", "end-1c").strip()
        if not user_input:
            logging.warning("Submit clicked with empty input.")
            return

        self.submit_button.config(state=tk.DISABLED)  # Disable submit button
        self.cancel_button.config(state=tk.NORMAL)  # Enable cancel button

        # Build the full prompt including context (codebase, tips)
        self.full_prompt = self.build_full_prompt(user_input)

        # Prepare message history for the agent
        # Start with base system prompt + summary
        messages = load_message_template('base', self.summary)

        # Add conversation history if enabled
        if self.conversation_history_enabled.get() and self.conversation_history:
            history_context = "\n".join(
                [f"User: {turn['user']}\nAssistant: {turn['assistant']}"
                 for turn in self.conversation_history]
            )
            # Add history context to the system message (or as separate messages?)
            # Adding to system message might exceed context limits faster.
            # Let's try adding as prior turns (limiting length might be needed)
            # Limit history to keep prompt size manageable
            history_limit = 2  # Keep last N turns
            limited_history = self.conversation_history[-history_limit:]
            for turn in limited_history:
                messages.append({'role': 'user', 'content': turn['user']})
                messages.append(
                     {'role': 'assistant', 'content': turn['assistant']})
            logging.info(
                f"Added {len(limited_history)} turns of conversation history to prompt.")

        # Add the current user request
        current_user_prompt = {'role': 'user', 'content': self.full_prompt}
        messages.append(current_user_prompt)

        # --- Logging and UI updates ---
        # Display combined context + prompt in interaction output for clarity
        full_input_for_log = "\n---\n".join(
            [f"Role: {m['role']}\n{m['content']}" for m in messages])
        self.update_interaction_output(
            "Agent Input Context", full_input_for_log)

        # Update user input history display
        self.update_user_input_history(user_input)  # Pass current input

        # Clear previous outputs
        self.output_text_area.delete("1.0", tk.END)
        self.agent_scratchpad_text_area.delete("1.0", tk.END)

        # Reset input history navigation index
        self.history_index = None
        # Reset auto-fill flag
        self.auto_prompt_set = False

        # --- Start Agent Execution ---
        # Note: decide_execution now expects the *list* of messages, not just the last user prompt dict
        self.run_async_in_thread(
            self.agent_executor.agent_execution(  # Pass the full message list
                messages, self.output_text_area, self.agent_scratchpad_text_area, self.root
            ),
            self.handle_response
        )

    def handle_response(self, response_tuple: Union[Tuple[str, str], str]) -> None:
        """Callback function to handle the response from the agent executor."""

        # Check if the response indicates an error from run_async_in_thread itself
        if isinstance(response_tuple, str) and response_tuple.startswith("Error:"):
            final_response = response_tuple
            action_log = "Execution failed within the async thread."
            logging.error(f"Async execution failed: {final_response}")
        elif isinstance(response_tuple, tuple) and len(response_tuple) == 2:
            final_response, action_log = response_tuple
            logging.info("Agent execution completed.")
        else:
            final_response = "Received unexpected response format from agent execution."
            action_log = f"Unexpected response: {response_tuple}"
            logging.error(final_response)

        # Update conversation history
        # Get the user input that triggered this response (it's the last one in text_history)
        last_user_input = self.text_history[-1] if self.text_history else ""
        self.conversation_history.append(
            {"user": last_user_input, "assistant": final_response}
        )

        # Display final response in the main output area
        self.output_text_area.insert(tk.END, final_response)

        # Log assistant's final response
        self.update_interaction_output("Assistant (Final)", final_response)

        # Display the action log
        self.action_output_area.config(state=tk.NORMAL)
        self.action_output_area.delete("1.0", tk.END)
        self.action_output_area.insert(tk.END, action_log)
        self.action_output_area.config(state=tk.DISABLED)

        # Summarize conversation periodically if enabled
        if self.conversation_history_enabled.get() and len(self.conversation_history) > 0 and \
           len(self.conversation_history) % self.conversation_turns == 0:
            self.summarize_conversation()

        # Re-enable submit button, disable cancel button
        self.submit_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

    def build_full_prompt(self, user_input: str) -> str:
        """Builds the user's part of the prompt including codebase and tips."""
        codebase_path = self.codebase_path_entry.get().strip()
        base_code = ""
        # Check if it's a valid directory
        if codebase_path and os.path.isdir(codebase_path):
            logging.info(f"Reading codebase from: {codebase_path}")
            try:
                # Use utils.code_corpus to get formatted code strings
                base_code_list = utils.code_corpus(codebase_path)
                base_code = "\n".join(base_code_list)
                if not base_code:
                    logging.warning(
                        f"No Python files found or read in directory: {codebase_path}")
            except Exception as e:
                logging.error(
                    f"Error reading codebase from {codebase_path}: {e}")
                # Optionally inform user in UI? For now, just log.
        elif codebase_path:
            logging.warning(
                f"Provided codebase path is not a valid directory: {codebase_path}")

        tips = self.tips_entry.get("1.0", "end-1c").strip()

        # Construct the prompt, adding sections only if they have content
        prompt_parts = []
        # Always include the request
        prompt_parts.append(f"{MD_HEADING} Request:\n{user_input}")

        if base_code:
            # Add codebase at the beginning if present
            prompt_parts.insert(
                0, f"{MD_HEADING} Codebase Context:\n{base_code}")

        if tips:
            # Add tips at the end if present
            prompt_parts.append(f"\n{MD_HEADING} Additional Tips:\n{tips}")

        full_prompt_text = "\n\n".join(prompt_parts)
        # logging.debug(f"Built full prompt:\n{full_prompt_text[:500]}...") # Log snippet
        return full_prompt_text

    def update_user_input_history(self, current_input: str) -> None:
        """Adds current input to history list and updates the display."""
        if not current_input:
            return

        self.text_history.append(current_input)
        # Optional: Limit history size
        max_history = 50
        if len(self.text_history) > max_history:
            self.text_history = self.text_history[-max_history:]

        # Update the ScrolledText widget
        try:
            if self.user_history.winfo_exists():
                self.user_history.config(state=tk.NORMAL)
                self.user_history.delete("1.0", tk.END)
                # Display history with numbers, newest last
                history_display = "\n".join(
                    f"{i+1}: {entry}" for i, entry in enumerate(reversed(self.text_history)))
                self.user_history.insert(tk.END, history_display)
                self.user_history.config(state=tk.DISABLED)
                self.user_history.see("1.0")  # Scroll to top (most recent)
        except tk.TclError as e:
            logging.warning(f"Failed to update user history display: {e}")

    def on_up_key(self, event) -> str:
        """Handler for the Up arrow key to recall previous input."""
        if not self.text_history:
            return "break"  # Indicates Tkinter should not process further

        if self.history_index is None:
            # Start from the most recent entry
            self.history_index = len(self.text_history) - 1
        elif self.history_index > 0:
            # Move to the previous (older) entry
            self.history_index -= 1
        else:
            # Already at the oldest entry
            return "break"

        # Display the recalled history item
        self.input_text_area.delete("1.0", tk.END)
        self.input_text_area.insert(
            "1.0", self.text_history[self.history_index])
        return "break"  # Prevent default Up key behavior

    def check_input(self) -> None:
        """
        Periodically checks for user inactivity and potentially auto-fills a prompt.
        (Currently set to check every 60 seconds).
        """
        # This auto-fill feature might be intrusive, consider making it optional or less frequent.
        check_interval_ms = 60000  # 60 seconds

        current_input = ""
        try:
            if self.input_text_area.winfo_exists():
                current_input = self.input_text_area.get(
                    "1.0", "end-1c").strip()
        except tk.TclError:
            logging.info("Input area check skipped, widget destroyed.")
            return  # Stop checking if widget is gone

        # Check if input is empty AND submit button is enabled (i.e., not currently processing)
        submit_state = self.submit_button.cget(
            'state') if self.submit_button.winfo_exists() else 'disabled'

        if not current_input and not self.auto_prompt_set and submit_state == tk.NORMAL:
            if self.first_check:
                logging.info(
                    f"No input detected for {check_interval_ms // 1000}s. Scheduling auto-prompt.")
                # Run auto-fill in a separate thread to avoid blocking GUI
                threading.Thread(target=lambda: asyncio.run(
                    self.auto_fill_and_submit_prompt()), daemon=True).start()
            else:
                # First time checking after startup or submission, just set the flag
                self.first_check = True
                logging.info("Input check: Initial check passed.")
        elif current_input:
            # If user has typed something, reset the first_check flag
            self.first_check = False
            self.auto_prompt_set = False  # Also reset auto_prompt flag if user interacted
            # logging.debug("Input check: User input detected.") # Less verbose log

        # Schedule the next check only if the root window still exists
        if self.root.winfo_exists():
            self.root.after(check_interval_ms, self.check_input)

    async def auto_fill_and_submit_prompt(self) -> None:
        """Generates a suggestion and fills the input area, then schedules submission."""
        if self.auto_prompt_set:  # Avoid race conditions
            return

        logging.info("Generating auto-prompt suggestion...")
        self.auto_prompt_set = True  # Set flag early

        # Define the base path for code corpus more robustly
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))  # Should point to project root
        simple_dir = os.path.join(base_dir, 'simple')

        base_code = ""
        if os.path.isdir(simple_dir):
            base_code = "".join(code_corpus(simple_dir))
        else:
            logging.warning(
                f"Auto-prompt: 'simple' directory not found at {simple_dir}")

        if not base_code:
            base_prompt_content = "Suggest a creative task for an AI agent."
        else:
            # Keep prompt concise
            base_prompt_content = f"## Codebase Context (summary):\n{base_code[:1000]}...\n\n## Task: Suggest one specific, actionable improvement for this codebase that could be performed by an AI agent using tools or Python code."

        prompt_messages = load_message_template(
            'base', '')  # Use base template for suggestion
        prompt_messages.append(
            {'role': 'user', 'content': base_prompt_content})

        # Run inference to get the suggestion
        # Use a temporary scratchpad update mechanism if desired, or None
        suggestion = run_inference(
            # No scratchpad update for this internal call
            prompt_messages, None, self.root, self.model_var.get())

        if not suggestion or suggestion.startswith("Error"):
            logging.error(
                f"Failed to generate auto-prompt suggestion: {suggestion}")
            self.auto_prompt_set = False  # Reset flag on failure
            return

        # Function to update GUI from this thread via root.after
        def _update_gui_with_suggestion():
            if not self.root.winfo_exists():
                return
            try:
                self.input_text_area.delete("1.0", tk.END)
                self.input_text_area.insert(tk.END, suggestion.strip())
                logging.info(f"Auto-filled prompt: {suggestion.strip()}")
                 # Schedule the actual submission after a short delay (e.g., 1 second)
                self.root.after(1000, self.submit_text)
            except tk.TclError as e:
                logging.warning(
                    f"Failed to update GUI with auto-prompt (window closed?): {e}")
                self.auto_prompt_set = False  # Reset flag

        # Schedule the GUI update in the main thread
        if self.root.winfo_exists():
            self.root.after(0, _update_gui_with_suggestion)
        else:
            self.auto_prompt_set = False  # Reset flag if root gone

    def summarize_conversation(self) -> None:
        """Summarizes the recent conversation history."""
        if not self.conversation_history:
            logging.info("No conversation history to summarize.")
            return

        # Get recent turns for summary
        history_to_summarize = self.conversation_history[-self.conversation_turns:]
        history_text = "\n".join([
            f"User: {turn['user']}\nAssistant: {turn['assistant']}"
            for turn in history_to_summarize
        ])

        # Prepare the summarization prompt
        summary_prompt_messages = load_message_template(
            'summary', '')  # Get summary system prompt
        summary_prompt_messages.append(
            {'role': 'user', 'content': history_text})

        logging.info(
            f"Summarizing last {len(history_to_summarize)} conversation turns...")
        self.update_interaction_output(
            "System", "Summarizing conversation...")  # UI feedback

        def handle_summary_result(summary_result: Union[Tuple[str, str], str]) -> None:
            """Callback to process the summary result."""
            if isinstance(summary_result, str) and summary_result.startswith("Error:"):
                summary = f"Failed to summarize conversation: {summary_result}"
                logging.error(summary)
            elif isinstance(summary_result, tuple):
                summary = summary_result[0]  # First element is the response
                logging.info(f"Conversation summarized successfully.")
                 # Replace history with summary (or keep summary separate?)
                 # For now, just store the summary and clear the history used for it.
                self.summary = summary
                 # Clear only the summarized part, keep newer turns if any added during summary
                self.conversation_history = self.conversation_history[len(
                     history_to_summarize):]
                logging.info(f"Stored summary: {self.summary[:100]}...")
                self.update_interaction_output(
                     "System", f"Conversation Summary:\n{self.summary}")
            else:
                summary = "Unexpected summary result format."
                logging.error(summary)

            # Update UI or internal state with the summary
            # (self.summary is updated internally)

        # Use run_async_in_thread for the summarization call
        # Note: summarize_conversation is called within handle_response, which is already in the main thread.
        # However, the actual inference for summarization should be async.
        # decide_execution is not ideal here as it triggers the full agent loop.
        # We need a way to just run inference. Let's call run_inference directly.

        # Define the async task for summarization inference
        async def _summarize_task():
            return run_inference(summary_prompt_messages, None, self.root, self.model_var.get())

        # Run the summarization task in a background thread
        self.run_async_in_thread(_summarize_task(), handle_summary_result)

    def on_closing(self) -> None:
        """Handles the event when the user closes the Tkinter window."""
        logging.info("Application window closing...")
        print("Shutting down FlexiAI...")

        # 1. Cancel any ongoing inference
        self.cancel_inference()

        # 2. Signal the Pygame simulation thread to stop
        if self.agent_manager:
            self.agent_manager.stop_game()

        # 3. Optionally wait for threads? (Daemon threads should exit automatically)
        #    For cleaner shutdown, one might join non-daemon threads here.

        # 4. Destroy the Tkinter window and exit the main loop
        self.root.destroy()
        print("FlexiAI shutdown complete.")


# Global reference to the app instance for the signal handler
_app_instance = None


def signal_handler(app: FlexiAgentApp, sig, frame):
    """Handles termination signals like SIGINT (Ctrl+C)."""
    print(f"\nReceived signal {sig}. Shutting down...")
    logging.info(f"Received signal {sig}. Initiating shutdown.")
    if app:
        # Trigger the same closing logic as the window close button
        app.on_closing()
    else:
        # If app instance isn't available, try basic cleanup
        if 'agent_manager' in locals() or 'agent_manager' in globals():
            try:
                 # Attempt to access manager if possible (less reliable)
                manager = locals().get('agent_manager') or globals().get('agent_manager')
                if manager:
                     manager.stop_game()
            except Exception as e:
                print(
                    f"Error stopping agent manager during signal handling: {e}")
        # Exit the process
        sys.exit(0)


def main() -> None:
    """Main function to initialize and run the application."""
    global _app_instance

    # Set up signal handling for graceful shutdown on Ctrl+C
    # Pass the app instance to the handler using a lambda
    def main_signal_handler(sig, frame):
        if _app_instance:
             signal_handler(_app_instance, sig, frame)
        else:
            print(
                 f"\nReceived signal {sig} before app fully initialized. Exiting.")
            sys.exit(0)

    signal.signal(signal.SIGINT, main_signal_handler)
    signal.signal(signal.SIGTERM, main_signal_handler)  # Handle termination signal

    # Initialize Tkinter
    root = tk.Tk()
    app = FlexiAgentApp(root)
    _app_instance = app  # Store instance globally for signal handler

    # Start the Tkinter main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        # This might catch Ctrl+C if signal handler doesn't exit fully
        print("\nKeyboardInterrupt caught in mainloop. Forcing exit.")
         # Ensure cleanup if signal handler didn't complete
        if _app_instance:
            _app_instance.on_closing()  # Attempt cleanup again
        sys.exit(1)


if __name__ == '__main__':
    main()
