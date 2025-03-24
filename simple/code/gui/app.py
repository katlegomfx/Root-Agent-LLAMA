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
from typing import Any

from simple.code import utils
from simple.code.utils import colored_print, Fore
from simple.code.logging_config import setup_logging
from simple.code.agent_executor import AgentExecutor
from simple.code.system_prompts import MD_HEADING, load_message_template
from simple import agent_interactions

setup_logging()


class FlexiAgentApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Flexi💻AI")
        self.set_app_icon()
        self.summary = ""
        self.text_history = []
        self.history_index = None  # Pointer for cycling through input history
        self.model_var = tk.StringVar(value="llama3.2")
        self.full_prompt = ""
        self.auto_prompt_set = False  # Flag to avoid multiple auto-fills
        self.first_check = False

        # Instantiate the agent executor
        self.agent_executor = AgentExecutor(model_name=self.model_var.get())

        self.build_gui()
        # Start periodic input check (every 60 seconds)
        self.check_input()
        # Bind the Up arrow to recall previous input when input area is focused
        self.input_text_area.bind("<Up>", self.on_up_key)
        # Optionally, you could add a Down arrow binding to cycle forward:
        # self.input_text_area.bind("<Down>", self.on_down_key)

    def build_gui(self) -> None:
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Right frame: Interaction Output
        right_frame = tk.Frame(frame, bg="lightgray")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(right_frame, text="Interaction Output", bg="lightgray", font=(
            "Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.interaction_output_area = ScrolledText(
            right_frame, state=tk.DISABLED, bg="white", width=40)
        self.interaction_output_area.grid(
            row=1, column=0, padx=5, pady=5, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Left frame: Input, Output, Scratchpad, and History
        left_frame = tk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 5))

        self.agent_interaction_button = tk.Button(
            left_frame, text="Show Agent Interaction", command=agent_interactions.launch_agent_interaction)
        self.agent_interaction_button.pack(pady=(0, 5))

        self.build_directory_and_tips(left_frame)
        self.build_input_area(left_frame)
        self.build_output_area(left_frame)
        self.build_scratchpad_area(left_frame)
        self.build_history_area(left_frame)

    def build_directory_and_tips(self, parent: tk.Frame) -> None:
        directory_frame = tk.Frame(parent)
        directory_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(directory_frame, text="Agent Work Directory:").grid(
            row=0, column=0, sticky="w")
        self.codebase_path_entry = tk.Entry(directory_frame)
        self.codebase_path_entry.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Label(directory_frame, text="Additional Tips:").grid(
            row=1, column=0, sticky="w")
        self.tips_entry = tk.Text(directory_frame, height=3)
        self.tips_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        directory_frame.grid_columnconfigure(1, weight=1)

    def build_input_area(self, parent: tk.Frame) -> None:
        input_frame = tk.Frame(parent)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(input_frame, text="Enter your request:").pack(anchor="w")
        self.input_text_area = tk.Text(input_frame, height=5)
        self.input_text_area.pack(fill=tk.BOTH, expand=True)
        self.submit_button = tk.Button(
            parent, text="Submit", command=self.submit_text)
        self.submit_button.pack(pady=(0, 5))

    def build_output_area(self, parent: tk.Frame) -> None:
        output_frame = tk.Frame(parent)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(output_frame, text="Output:").pack(anchor="w")
        self.output_text_area = ScrolledText(
            output_frame, height=10, bg="lightyellow")
        self.output_text_area.pack(fill=tk.BOTH, expand=True)

    def build_scratchpad_area(self, parent: tk.Frame) -> None:
        scratchpad_frame = tk.Frame(parent)
        scratchpad_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(scratchpad_frame, text="Scratchpad:").pack(anchor="w")
        self.agent_scratchpad_text_area = ScrolledText(
            scratchpad_frame, height=10, bg="lightgray")
        self.agent_scratchpad_text_area.pack(fill=tk.BOTH, expand=True)

    def build_history_area(self, parent: tk.Frame) -> None:
        history_frame = tk.Frame(parent)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(history_frame, text="User History:").pack(anchor="w")
        self.user_history = ScrolledText(
            history_frame, height=10, state=tk.DISABLED, bg="lightblue")
        self.user_history.pack(fill=tk.BOTH, expand=True)

    def update_interaction_output(self, role: str, content: str) -> None:
        formatted_text = f"Role: {role}\nContent:\n{content}\n{'-'*40}\n"
        self.interaction_output_area.config(state=tk.NORMAL)
        self.interaction_output_area.insert(tk.END, formatted_text)
        self.interaction_output_area.see(tk.END)
        self.interaction_output_area.config(state=tk.DISABLED)

    def set_app_icon(self) -> None:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.normpath(os.path.join(
                current_dir, "..", "gag", "artistic_plot.png"))
            if not os.path.exists(icon_path):
                from simple.makeArt import create_artistic_png
                default_data = [1, 3, 2, 5, 7, 8, 6]
                create_artistic_png(default_data, filename=icon_path)
                logging.info(
                    f"Icon file not found. Generated new icon at: {icon_path}")
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
        except Exception as e:
            logging.error(f"Failed to load custom icon: {e}")

    def run_async_in_thread(self, coroutine: Any, callback: Any) -> None:
        def worker() -> None:
            try:
                result = asyncio.run(coroutine)
            except Exception as e:
                logging.exception("Error in asynchronous coroutine")
                result = f"Error: {str(e)}"
            self.root.after(0, callback, result)
        threading.Thread(target=worker, daemon=True).start()

    def submit_text(self) -> None:
        user_input = self.input_text_area.get("1.0", "end-1c")
        if not user_input.strip():
            return
        # Build the full prompt from user input and any extra context
        self.full_prompt = self.build_full_prompt(user_input)
        # Load the system message from load_message_template (base type)
        system_msgs = load_message_template('base', '')
        system_text = "\n".join([msg["content"] for msg in system_msgs])
        full_input_text = system_text + "\n" + self.full_prompt
        # Show the full input (system message + user request) in the interaction output
        self.update_interaction_output("Full Input", full_input_text)
        # Also show the user's raw input
        self.update_interaction_output("User", user_input)
        self.agent_executor.full_prompt = self.full_prompt
        self.submit_button.config(state=tk.DISABLED)
        self.text_prompt = {'role': 'user', 'content': self.full_prompt}
        self.update_user_input_history()
        self.output_text_area.delete("1.0", tk.END)
        self.agent_scratchpad_text_area.delete("1.0", tk.END)
        # Reset history index after a new submission
        self.history_index = None
        self.run_async_in_thread(
            self.agent_executor.decide_execution(
                self.text_prompt, self.output_text_area, self.agent_scratchpad_text_area, self.root, self.full_prompt
            ),
            self.handle_response
        )
        self.auto_prompt_set = False  # Reset auto-fill flag upon submission

    def handle_response(self, response: str) -> None:
        self.text_prompt = [self.text_prompt, {
            'role': 'assistant', 'content': response}]
        self.update_interaction_output("Assistant", response)
        self.submit_button.config(state=tk.NORMAL)

    def build_full_prompt(self, user_input: str) -> str:
        codebase_path = self.codebase_path_entry.get().strip()
        base_code = ""
        if codebase_path:
            try:
                base_code_list = utils.code_corpus(codebase_path)
                base_code = "\n".join(base_code_list)
            except Exception as e:
                logging.error(f"Error reading codebase: {e}")
        tips = self.tips_entry.get("1.0", "end-1c").strip()
        if base_code and tips:
            full_prompt = f"{MD_HEADING} Codebase:\n{base_code}\n\n{MD_HEADING} Request:\n{user_input}\n\nTips:\n{tips}"
        elif base_code:
            full_prompt = f"{MD_HEADING} Codebase:\n{base_code}\n\n{MD_HEADING} Request:\n{user_input}"
        elif tips:
            full_prompt = f"{MD_HEADING} Request:\n{user_input}\n\nTips:\n{tips}"
        else:
            full_prompt = f"{MD_HEADING} Request:\n{user_input}"
        return full_prompt

    def update_user_input_history(self) -> None:
        self.text_history.append(self.input_text_area.get("1.0", "end-1c"))
        self.user_history.config(state=tk.NORMAL)
        self.user_history.delete("1.0", tk.END)
        self.user_history.insert(tk.END, "\n".join(self.text_history))
        self.user_history.config(state=tk.DISABLED)

    def on_up_key(self, event) -> str:
        """Handler for the Up arrow key to recall previous input."""
        if not self.text_history:
            return "break"
        if self.history_index is None:
            self.history_index = len(self.text_history) - 1
        else:
            if self.history_index > 0:
                self.history_index -= 1
        self.input_text_area.delete("1.0", tk.END)
        self.input_text_area.insert(
            "end", self.text_history[self.history_index])
        return "break"

    def check_input(self) -> None:
        """
        Checks every 60 seconds if the user has entered any text in the input area.
        If no input is present and no auto-prompt has been set, update the prompt to a random one and schedule submission.
        """
        current_input = self.input_text_area.get("1.0", "end-1c").strip()
        if not current_input and not self.auto_prompt_set:
            if self.first_check:
                logging.info(
                    "No input detected. Auto-filling prompt in 60 seconds.")
                self.auto_fill_and_submit_prompt()
            else:
                self.first_check = True
        else:
            logging.info("User input detected.")
        # Schedule the next check in 60 seconds (60000 milliseconds)
        self.root.after(60000, self.check_input)

    def auto_fill_and_submit_prompt(self) -> None:
        """
        Updates the input area with a random prompt from a list of 12 prompts
        focused on improving the codebase, then waits 60 seconds and submits it.
        """
        prompts = [
            "Refactor the agent_interactions module to reduce code duplication.",
            "Improve error handling in the tool execution functions.",
            "Enhance the logging configuration for better debugging output.",
            "Modularize the code execution logic to separate concerns.",
            "Optimize the Tkinter GUI layout for responsiveness.",
            "Streamline the agent_executor logic to simplify JSON extraction.",
            "Add unit tests for the tool registry and custom tools.",
            "Improve code documentation and inline comments throughout the codebase.",
            "Refactor the code to use more efficient data structures where possible.",
            "Consolidate repeated functionality in the GUI helper methods.",
            "Implement a more robust mechanism for asynchronous code execution.",
            "Review and optimize the performance of the inference client."
        ]
        prompt = random.choice(prompts)
        self.input_text_area.delete("1.0", tk.END)
        self.input_text_area.insert(tk.END, prompt)
        logging.info(f"Auto-filled prompt: {prompt}")
        self.auto_prompt_set = True
        # Schedule auto-submission in 60 seconds (60000 milliseconds)
        self.root.after(60000, self.submit_text)


def main() -> None:
    root = tk.Tk()
    app = FlexiAgentApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
