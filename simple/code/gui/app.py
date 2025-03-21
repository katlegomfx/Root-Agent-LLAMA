# Agentic System

# Process
# - Agentic System capable for running tools and executing code
# - the system should decide if it should get information from the vector database
# - the tool or code should get executed

# GUI
# - input text area for user to enter what they would like to do
# - text area scratchpad for run inference to show each step taken
# - the agent should work on the task in the scratchpad continuously until the retries run out or the task is complete
# - the final response should be written to the output area
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

from simple.code import utils
from simple.code.utils import colored_print, Fore
from simple.code.logging_config import setup_logging
from simple.code.agent_executor import AgentExecutor
from simple.code.system_prompts import MD_HEADING

setup_logging()


class FlexiAgentApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Flexi💻AI")
        self.set_app_icon()
        self.summary = ""
        self.text_history = []
        self.model_var = tk.StringVar(value="llama3.2")

        # Instantiate the agent executor with the current model
        self.agent_executor = AgentExecutor(model_name=self.model_var.get())

        # Main container with padding
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Right frame: Interaction Output
        right_frame = tk.Frame(frame, bg="lightgray")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(right_frame, text="Interaction Output", bg="lightgray",
                 font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.interaction_output_area = ScrolledText(
            right_frame, state=tk.DISABLED, bg="white", width=40)
        self.interaction_output_area.grid(
            row=1, column=0, padx=5, pady=5, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Left frame: Input, Output, Scratchpad, and History
        left_frame = tk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 5))

        # Directory and Tips
        directory_frame = tk.Frame(left_frame)
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

        # User Request Input
        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(input_frame, text="Enter your request:").pack(anchor="w")
        self.input_text_area = tk.Text(input_frame, height=5)
        self.input_text_area.pack(fill=tk.BOTH, expand=True)

        # Submit Button
        self.submit_button = tk.Button(
            left_frame, text="Submit", command=self.submit_text)
        self.submit_button.pack(pady=(0, 5))

        # Output Area
        output_frame = tk.Frame(left_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(output_frame, text="Output:").pack(anchor="w")
        self.output_text_area = ScrolledText(
            output_frame, height=10, bg="lightyellow")
        self.output_text_area.pack(fill=tk.BOTH, expand=True)

        # Scratchpad Area
        scratchpad_frame = tk.Frame(left_frame)
        scratchpad_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(scratchpad_frame, text="Scratchpad:").pack(anchor="w")
        self.agent_scratchpad_text_area = ScrolledText(
            scratchpad_frame, height=10, bg="lightgray")
        self.agent_scratchpad_text_area.pack(fill=tk.BOTH, expand=True)

        # User History Area (read-only)
        history_frame = tk.Frame(left_frame)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(history_frame, text="User History:").pack(anchor="w")
        self.user_history = ScrolledText(
            history_frame, height=10, state=tk.DISABLED, bg="lightblue")
        self.user_history.pack(fill=tk.BOTH, expand=True)

    def update_interaction_output(self, role: str, content: str) -> None:
        formatted_text = f"Role: {role}\nContent: {content}\n{'-'*40}\n"
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

    def run_async_in_thread(self, coroutine, callback):
        def worker():
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
        self.update_interaction_output("User", user_input)
        self.full_prompt = self.build_full_prompt(user_input)
        # Pass the full prompt to the agent executor
        self.agent_executor.full_prompt = self.full_prompt
        self.submit_button.config(state=tk.DISABLED)
        self.text_prompt = {'role': 'user', 'content': self.full_prompt}
        self.update_user_input_history()
        self.output_text_area.delete("1.0", tk.END)
        self.agent_scratchpad_text_area.delete("1.0", tk.END)
        # Run the agent execution asynchronously
        self.run_async_in_thread(
            self.agent_executor.decide_execution(self.text_prompt),
            self.handle_response
        )

    def handle_response(self, response: str) -> None:
        self.text_prompt = [self.text_prompt]
        self.text_prompt.append({'role': 'assistant', 'content': response})
        self.output_text_area.insert(tk.END, "\n" + response)
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


def main() -> None:
    root = tk.Tk()
    app = FlexiAgentApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
