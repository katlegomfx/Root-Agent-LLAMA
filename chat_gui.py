import tkinter as tk
from tkinter import filedialog
import threading
import asyncio
import json
import re
import io
import contextlib
from datetime import datetime
import os
import tempfile
import subprocess
import logging
from typing import List

from simple.code import utils, memory
from simple.code.inference import run_inference, current_client
from simple.code.history import HistoryManager
from simple.code.system_prompts import MD_HEADING, load_message_template

logging.basicConfig(level=logging.INFO)


# Helper class to update two text widgets simultaneously.
class DualTextWidget:
    def __init__(self, widget1, widget2):
        self.widget1 = widget1
        self.widget2 = widget2

    def insert(self, index, text):
        self.widget1.insert(index, text)
        self.widget2.insert(index, text)

    def see(self, index):
        self.widget1.see(index)
        self.widget2.see(index)


def apply_theme_recursive(widget, bg_color, fg_color):
    """Recursively apply background and foreground colors to widget and its children."""
    try:
        widget.configure(bg=bg_color, fg=fg_color)
    except tk.TclError:
        pass
    for child in widget.winfo_children():
        apply_theme_recursive(child, bg_color, fg_color)


class CollapsibleSection(tk.Frame):
    def __init__(self, master, title="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.show = tk.BooleanVar(value=True)
        self.header_frame = tk.Frame(self)
        self.header_frame.pack(fill="x")
        self.toggle_button = tk.Button(
            self.header_frame, text="-", command=self.toggle, width=2)
        self.toggle_button.pack(side="left")
        self.title_label = tk.Label(
            self.header_frame, text=title, font=("Arial", 12, "bold"))
        self.title_label.pack(side="left", fill="x", padx=5)
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill="both", expand=True)

    def toggle(self) -> None:
        if self.show.get():
            self.content_frame.forget()
            self.toggle_button.configure(text="+")
            self.show.set(False)
        else:
            self.content_frame.pack(fill="both", expand=True)
            self.toggle_button.configure(text="-")
            self.show.set(True)


class FlexiAIApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Flexi💻AI")
        self.root.geometry("600x1000")
        self.is_dark_mode = False
        self.set_app_icon()
        self.collapsible_sections = []
        self.all_sections_expanded = True

        # Add a variable for the agent goal (to be specified by the user)
        self.agent_goal = ""

        self.text_prompt = [{
            'role': 'system',
            'content': "You are Flexi💻AI. You think step by step, keeping key points in mind to solve or answer the request."
        }]
        self.user_input_history = []
        self.user_input_history_index = None
        self.assistant_response_history = []
        self.assistant_response_history_index = None
        self.current_history_file = ""

        self.history_manager = HistoryManager()
        self.model_map = {'llama3.2': ()}
        self.setup_ui()
        self.auto_save_interval_ms = 5 * 60 * 1000
        self.schedule_auto_save()
        self.load_first_history()

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

    def load_first_history(self) -> None:
        """Automatically load the first history file found, if any."""
        history_files = self.history_manager.get_history_files()
        if history_files:
            first_history = history_files[0]
            loaded_history = self.history_manager.load_history(first_history)
            if loaded_history:
                self.text_prompt = loaded_history
                self.current_history_file = first_history
                if self.text_prompt and self.text_prompt[0].get("role") == "system":
                    self.system_text_area.delete("1.0", tk.END)
                    self.system_text_area.insert(
                        "1.0", self.text_prompt[0]["content"])
                self.update_user_input_history()
                self.update_assistant_response_history()
                logging.info(f"Loaded history from {first_history}")

    def search_history(self) -> None:
        """Opens a dialog to search conversation history and display matching entries."""
        def do_search():
            query = search_entry.get().strip().lower()
            results.delete(0, tk.END)
            # Combine user and assistant messages
            matching = [line for line in self.text_prompt if query in line.get(
                "content", "").lower()]
            if not matching:
                results.insert(tk.END, "No matching entries found.")
            else:
                for idx, entry in enumerate(matching, start=1):
                    # Display a truncated version for brevity
                    content = entry.get("content", "")
                    results.insert(tk.END, f"{idx}: {content[:80]}...")

        search_window = tk.Toplevel(self.root)
        search_window.title("Search Conversation History")
        tk.Label(search_window, text="Enter search query:").pack(
            padx=5, pady=5)
        search_entry = tk.Entry(search_window, width=50)
        search_entry.pack(padx=5, pady=5)
        tk.Button(search_window, text="Search",
                  command=do_search).pack(padx=5, pady=5)
        results = tk.Listbox(search_window, width=100, height=10)
        results.pack(padx=5, pady=5, fill="both", expand=True)

    def setup_ui(self) -> None:
        top_bar = tk.Frame(self.root)
        top_bar.pack(fill="x", padx=5, pady=5)
        tk.Button(top_bar, text="Toggle Theme",
                  command=self.toggle_theme).pack(side="right")
        tk.Button(top_bar, text="Toggle All",
                  command=self.toggle_all_sections).pack(side="left", padx=5)

        # # =======================
        # # New Agent Goal Section
        # agent_goal_section = CollapsibleSection(self.root, title="Agent Goal")
        # self.collapsible_sections.append(agent_goal_section)
        # agent_goal_frame = agent_goal_section.content_frame
        # tk.Label(agent_goal_frame, text="Specify Agent Goal:").grid(
        #     row=0, column=0, sticky="w", padx=5, pady=5)
        # self.agent_goal_entry = tk.Text(agent_goal_frame, height=3)
        # self.agent_goal_entry.grid(
        #     row=1, column=0, sticky="ew", padx=5, pady=5)
        # agent_goal_frame.grid_columnconfigure(0, weight=1)
        # # =======================
        model_section = CollapsibleSection(self.root, title="Model Selection")
        self.collapsible_sections.append(model_section)
        model_section.pack(fill="x", padx=5, pady=5)
        model_frame = model_section.content_frame
        tk.Label(model_frame, text="Select Model:").grid(
            row=0, column=0, sticky="w")
        model_options = list(self.model_map.keys()
                             ) if self.model_map else ["llama3.2"]
        self.model_var = tk.StringVar(model_frame, value=model_options[0])
        tk.OptionMenu(model_frame, self.model_var, *
                      model_options).grid(row=0, column=1, padx=5, pady=5)

        mode_section = CollapsibleSection(self.root, title="Execution Mode")
        self.collapsible_sections.append(mode_section)
        mode_section.pack(fill="x", padx=5, pady=5)
        mode_frame = mode_section.content_frame
        tk.Label(mode_frame, text="Select Mode:").grid(
            row=0, column=0, sticky="w")
        self.mode_var = tk.StringVar(mode_frame, value="base")
        mode_options = ["auto", "tool", "code", "base"]
        tk.OptionMenu(mode_frame, self.mode_var, *
                      mode_options).grid(row=0, column=1, padx=5, pady=5)
        mode_frame.grid_columnconfigure(1, weight=1)




        sp_mgmt_section = CollapsibleSection(
            self.root, title="System Prompt Management")
        self.collapsible_sections.append(sp_mgmt_section)
        sp_mgmt_section.pack(fill="x", padx=5, pady=5)
        sp_mgmt_frame = sp_mgmt_section.content_frame
        tk.Label(sp_mgmt_frame, text="System Prompts:").grid(
            row=0, column=0, sticky="w")
        self.system_prompt_var = tk.StringVar(sp_mgmt_frame)
        self.system_prompt_dropdown = tk.OptionMenu(
            sp_mgmt_frame, self.system_prompt_var, "")
        self.system_prompt_dropdown.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(sp_mgmt_frame, text="Load Prompt", command=self.load_system_prompt_file).grid(
            row=0, column=2, padx=5, pady=5)
        tk.Label(sp_mgmt_frame, text="Prompt Name:").grid(
            row=1, column=0, sticky="w")
        self.prompt_name_entry = tk.Entry(sp_mgmt_frame)
        self.prompt_name_entry.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(sp_mgmt_section.content_frame, text="Save as New",
                  command=self.save_system_prompt_as_new).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(sp_mgmt_section.content_frame, text="Delete Prompt",
                  command=self.delete_system_prompt_file).grid(row=1, column=3, padx=5, pady=5)
        sp_mgmt_frame.grid_columnconfigure(1, weight=1)
        self.update_system_prompts_dropdown()

        system_section = CollapsibleSection(self.root, title="System Prompt")
        self.collapsible_sections.append(system_section)
        system_section.pack(fill="x", padx=5, pady=5)
        system_frame = system_section.content_frame
        tk.Label(system_frame, text="System Prompt:").grid(
            row=0, column=0, sticky="w")
        self.system_text_area = tk.Text(system_frame, height=3)
        self.system_text_area.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.system_text_area.insert("1.0", self.text_prompt[0]["content"])
        tk.Button(system_frame, text="Update System Prompt",
                  command=self.update_system_prompt).grid(row=1, column=1, sticky="e")
        system_frame.grid_columnconfigure(0, weight=1)

        template_section = CollapsibleSection(
            self.root, title="Message Template")
        self.collapsible_sections.append(template_section)
        template_section.pack(fill="x", padx=5, pady=5)
        template_frame = template_section.content_frame
        tk.Label(template_frame, text="Template Type:").grid(
            row=0, column=0, sticky="w")
        self.template_var = tk.StringVar(template_frame, value="base")
        template_options = ["base", "check", "general", "bot", "tool",
                            "work", "projectSteps", "projectTasks", "projectProcess", "summary"]
        tk.OptionMenu(template_frame, self.template_var, *
                      template_options).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(template_frame, text="Summary Context (optional):").grid(
            row=1, column=0, sticky="w")
        self.template_summary = tk.Text(template_frame, height=2)
        self.template_summary.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(template_frame, text="Load Template", command=self.load_template).grid(
            row=0, column=2, padx=5, pady=5)
        template_frame.grid_columnconfigure(1, weight=1)



        history_section = CollapsibleSection(self.root, title="History")
        self.collapsible_sections.append(history_section)
        history_section.pack(fill="x", padx=5, pady=5)
        history_frame = history_section.content_frame
        tk.Label(history_frame, text="History Files:").grid(
            row=0, column=0, sticky="w")
        self.history_var = tk.StringVar(history_frame)
        history_files = self.history_manager.get_history_files()
        if history_files:
            self.history_var.set(history_files[0])
            self.history_dropdown = tk.OptionMenu(
                history_frame, self.history_var, *history_files)
        else:
            self.history_var.set("No history files")
            self.history_dropdown = tk.OptionMenu(
                history_frame, self.history_var, "No history files")
        self.history_dropdown.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(history_frame, text="Load History", command=self.load_history).grid(
            row=0, column=2, padx=5, pady=5)
        tk.Button(history_frame, text="Delete History", command=self.delete_history).grid(
            row=0, column=3, padx=5, pady=5)
        tk.Button(history_frame, text="View History", command=self.view_history).grid(
            row=0, column=4, padx=5, pady=5)
        tk.Label(history_frame, text="File Name:").grid(
            row=1, column=0, sticky="w", pady=5)
        self.history_filename_entry = tk.Entry(history_frame)
        self.history_filename_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(history_frame, text="Save History", command=self.save_history).grid(
            row=1, column=2, padx=5, pady=5)
        history_frame.grid_columnconfigure(0, weight=1)
        tk.Button(history_frame, text="Search History", command=self.search_history).grid(
            row=0, column=5, padx=5, pady=5)



        input_section = CollapsibleSection(self.root, title="Input")
        self.collapsible_sections.append(input_section)
        input_section.pack(fill="x", padx=5, pady=5)
        input_frame = input_section.content_frame
        self.input_text_area = tk.Text(input_frame, height=5)
        self.input_text_area.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        control_frame = tk.Frame(input_frame)
        control_frame.grid(row=0, column=1, sticky="ns")
        tk.Button(control_frame, text="↑",
                  command=self.show_previous_input).pack(fill="x")
        self.submit_button = tk.Button(
            control_frame, text="Submit", command=self.submit_text)
        self.submit_button.pack(fill="x")
        tk.Button(control_frame, text="↓",
                  command=self.show_next_input).pack(fill="x")
        tk.Button(control_frame, text="Cancel",
                  command=self.cancel_inference).pack(fill="x", pady=5)
        tk.Button(control_frame, text="Clear Conversation",
                  command=self.clear_conversation).pack(fill="x", pady=5)
        input_frame.grid_columnconfigure(0, weight=1)

        code_append_section = CollapsibleSection(
            self.root, title="Code Append")
        self.collapsible_sections.append(code_append_section)
        code_append_section.pack(fill="x", padx=5, pady=5)
        code_append_frame = code_append_section.content_frame
        tk.Label(code_append_frame, text="Codebase Directory:").grid(
            row=0, column=0, sticky="w")
        self.codebase_path_entry = tk.Entry(code_append_frame)
        self.codebase_path_entry.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Label(code_append_frame, text="Additional Tips:").grid(
            row=1, column=0, sticky="w")
        self.tips_entry = tk.Text(code_append_frame, height=3)
        self.tips_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        code_append_frame.grid_columnconfigure(1, weight=1)

        # =======================
        # New Scratchpad Section for incremental LLM output
        scratchpad_section = CollapsibleSection(self.root, title="Scratchpad")
        self.collapsible_sections.append(scratchpad_section)
        scratchpad_frame = scratchpad_section.content_frame
        tk.Label(scratchpad_frame, text="LLM Scratchpad (Intermediate Output):").pack(
            anchor="w", padx=5, pady=5)
        self.scratchpad_text_area = tk.Text(scratchpad_frame, height=10)
        self.scratchpad_text_area.pack(
            fill="both", expand=True, padx=5, pady=5)
        # =======================

        output_section = CollapsibleSection(self.root, title="Output")
        self.collapsible_sections.append(output_section)
        output_section.pack(fill="both", expand=True, padx=5, pady=5)
        output_frame = output_section.content_frame
        response_control_frame = tk.Frame(output_frame)
        response_control_frame.pack(fill="x")
        tk.Button(response_control_frame, text="Assistant ↑",
                  command=self.show_previous_response).pack(side="left", padx=5, pady=2)
        tk.Button(response_control_frame, text="Assistant ↓",
                  command=self.show_next_response).pack(side="left", padx=5, pady=2)
        output_scrollbar = tk.Scrollbar(output_frame)
        output_scrollbar.pack(side="right", fill="y")
        self.output_text_area = tk.Text(
            output_frame, yscrollcommand=output_scrollbar.set)
        self.output_text_area.pack(fill="both", expand=True)
        output_scrollbar.config(command=self.output_text_area.yview)

        code_extraction_section = CollapsibleSection(
            self.root, title="Code Extraction")
        self.collapsible_sections.append(code_extraction_section)
        code_extraction_section.pack(fill="x", padx=5, pady=5)
        code_extraction_frame = code_extraction_section.content_frame
        tk.Label(code_extraction_frame, text="Extract Code Snippets (Language):").grid(
            row=0, column=0, sticky="w")
        self.code_language_var = tk.StringVar(
            code_extraction_frame, value="python")
        tk.OptionMenu(code_extraction_frame, self.code_language_var,
                      "python", "bash", "json").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(code_extraction_frame, text="Extract Code",
                  command=self.extract_code_snippets).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(code_extraction_frame, text="Save Suggested Files",
                  command=self.save_suggested_files_from_output).grid(row=0, column=3, padx=5, pady=5)
        code_extraction_frame.grid_columnconfigure(0, weight=1)

    def toggle_all_sections(self) -> None:
        """Toggle expand/collapse state for all collapsible sections."""
        for section in self.collapsible_sections:
            if self.all_sections_expanded and section.show.get():
                section.toggle()
            elif not self.all_sections_expanded and not section.show.get():
                section.toggle()
        self.all_sections_expanded = not self.all_sections_expanded
        logging.info(
            f"All sections toggled. Expanded state now: {self.all_sections_expanded}")

    def load_template(self) -> None:
        template_type = self.template_var.get()
        summary_text = self.template_summary.get("1.0", "end-1c").strip()
        messages = load_message_template(template_type, summary_text)
        if messages:
            self.system_text_area.delete("1.0", tk.END)
            self.system_text_area.insert("1.0", messages[0]["content"])
            logging.info(
                f"Loaded '{template_type}' template with summary context.")

    def toggle_theme(self) -> None:
        self.is_dark_mode = not self.is_dark_mode
        bg_color = f"{MD_HEADING}2e2e2e" if self.is_dark_mode else "SystemButtonFace"
        fg_color = "white" if self.is_dark_mode else "black"
        self.root.configure(bg=bg_color)
        apply_theme_recursive(self.root, bg_color, fg_color)

    def schedule_auto_save(self) -> None:
        self.auto_save_history()
        self.root.after(self.auto_save_interval_ms, self.schedule_auto_save)

    def cancel_inference(self) -> None:
        global current_client
        if current_client:
            current_client.cancel()
            logging.info("Inference cancellation requested.")
        else:
            logging.info("No active inference to cancel.")

    def update_user_input_history(self) -> None:
        self.user_input_history = [msg["content"]
                                   for msg in self.text_prompt if msg.get("role") == "user"]
        self.user_input_history_index = None

    def update_assistant_response_history(self) -> None:
        self.assistant_response_history = [
            msg["content"] for msg in self.text_prompt if msg.get("role") == "assistant"]
        self.assistant_response_history_index = None

    def get_memory_context(self, user_request: str) -> str:
        """
        Retrieves a formatted memory context block based on the current user request.
        It leverages memory.create_queries() and memory.retrieve_embeddings() functions.
        Returns a string that can be prepended to the prompt.
        """
        memory_context = ""
        try:
            # Generate search queries from the current user request
            queries = memory.create_queries(user_request)
            # Retrieve relevant memory embeddings (returns a set of context strings)
            embeddings = memory.retrieve_embeddings(queries)
            if embeddings:
                # Join the embeddings into a single memory context block
                memory_context = f"\nMEMORIES: {', '.join(embeddings)}\n\n"
        except Exception as e:
            logging.error(f"Error retrieving memory: {e}")
        return memory_context

    def build_full_prompt(self, user_request: str) -> str:
        """
        Builds the full prompt to be sent for inference. This version enhances the prompt by:
        - Including codebase context (if a codebase path is provided)
        - Retrieving relevant memory (using functions from memory.py)
        - Appending any additional tips provided by the user
        - Incorporating the user-specified agent goal (if provided)
        """
        codebase_path = self.codebase_path_entry.get().strip()
        base_code = ""
        if codebase_path:
            try:
                base_code_list = utils.code_corpus(codebase_path)
                base_code = "\n".join(base_code_list)
            except Exception as e:
                logging.error(f"Error reading codebase: {e}")

        tips = self.tips_entry.get("1.0", "end-1c").strip()

        # --- Integrate memory retrieval ---
        memory_context = self.get_memory_context(user_request)
        # --- Build the final prompt ---
        if base_code != "" and tips != "":
            full_prompt = f"{MD_HEADING} Codebase:\n\n{base_code}\n\n{memory_context}{MD_HEADING} {user_request}\n\n{tips}"
        elif base_code != "":
            full_prompt = f"{MD_HEADING} Codebase:\n\n{base_code}\n\n{memory_context}{MD_HEADING} {user_request}"
        else:
            full_prompt = f"{memory_context}{MD_HEADING} {user_request}"

        # Prepend the agent goal if one has been specified
        agent_goal = self.agent_goal_entry.get("1.0", "end-1c").strip()
        if agent_goal:
            full_prompt = f"Goal: {agent_goal}\n\n{full_prompt}"
        return full_prompt

    @staticmethod
    def extract_code_blocks(text: str, language: str) -> list:
        pattern = rf"```{re.escape(language)}\s*\n(.*?)```"
        return re.findall(pattern, text, re.DOTALL)

    async def tool_use(self, base_prompt: List[dict]):
        base_response = run_inference(
            base_prompt, self.output_text_area, self.root, self.model_var.get())
        tool_script = self.extract_code_blocks(base_response, 'json')
        if not tool_script:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': json.dumps(base_response)})
            correction_prompt.append(
                {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json'."})
            return await self.tool_use(correction_prompt)
        status_messages = []
        for code_snippet in tool_script:
            try:
                json_instruct = json.loads(code_snippet)
            except json.JSONDecodeError:
                continue
            if isinstance(json_instruct, list):
                json_instruct = json_instruct[0]
            elif isinstance(json_instruct, str):
                correction_prompt = base_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                correction_prompt.append(
                    {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json' with an object containing tool and parameters."})
                return await self.tool_use(correction_prompt)
            status_message = execute_tool(json_instruct)
            if status_message['status'] != "200":
                new_prompt = base_prompt.copy()
                new_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                new_prompt.append(
                    {'role': 'user', 'content': f"{MD_HEADING} Generated tool instruction:\n\n{json.dumps(tool_script)}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}\n\n{MD_HEADING} Fix the above error"})
                return await self.tool_use(new_prompt)
            else:
                base_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                status_messages.append(status_message)
            final_prompt = base_prompt.copy()
            final_prompt.append(
                {'role': 'user', 'content': f"{MD_HEADING} Generated tool instruction:\n\n{code_snippet}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}"})
            final_response = run_inference(
                final_prompt, self.output_text_area, self.root, self.model_var.get())
            base_prompt.append(
                {'role': 'assistant', 'content': final_response})
            return final_response, tool_script, status_messages, base_prompt

    async def code_use(self, base_prompt: List[dict]):
        base_response = run_inference(
            base_prompt, self.output_text_area, self.root, self.model_var.get())
        code_script = self.extract_code_blocks(base_response, 'python')
        status_message = execute_python_code("".join(code_script))
        if status_message['status'] != "200":
            new_prompt = base_prompt.copy()
            new_prompt.append({'role': 'assistant', 'content': base_response})
            new_prompt.append(
                {'role': 'user', 'content': f"{MD_HEADING} Generated code:\n\n{''.join(code_script)}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}"})
            return await self.tool_use(new_prompt)
        else:
            base_prompt.append({'role': 'assistant', 'content': base_response})
            base_prompt.append(
                {'role': 'user', 'content': f"{MD_HEADING} Generated code:\n\n{''.join(code_script)}\n\n{MD_HEADING} Execution result:\n\n{status_message['message']}"})
            final_response = run_inference(
                base_prompt, self.output_text_area, self.root, self.model_var.get())
            base_prompt.append(
                {'role': 'assistant', 'content': final_response})
            return final_response, code_script, status_message, base_prompt

    async def decide_execution(self, base_prompt: List[dict]):
        base_response = run_inference(
            base_prompt, self.output_text_area, self.root, self.model_var.get())
        use_script = self.extract_code_blocks(base_response, 'json')
        if not use_script:
            correction_prompt = base_prompt.copy()
            correction_prompt.append(
                {'role': 'assistant', 'content': base_response})
            correction_prompt.append(
                {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json'. (start response with ```json)"})
            return await self.decide_execution(correction_prompt)
        for code_snippet in use_script:
            try:
                json_instruct = json.loads(code_snippet)
            except json.JSONDecodeError:
                continue
            if isinstance(json_instruct, list):
                json_instruct = json_instruct[0]
            elif isinstance(json_instruct, str):
                correction_prompt = base_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                correction_prompt.append(
                    {'role': 'user', 'content': "Remember to wrap the instruction in triple backticks and specify 'json' with an object containing the key 'use' and a 'value' either python or tool."})
                return await self.decide_execution(correction_prompt)
            if 'use' in json_instruct and json_instruct['use'].lower() in ['python', 'tool']:
                base_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                return json_instruct["use"].lower()
            else:
                correction_prompt = base_prompt.copy()
                correction_prompt.append(
                    {'role': 'assistant', 'content': json.dumps(base_response)})
                correction_prompt.append(
                    {'role': 'user', 'content': "Please produce a JSON object with 'use' key and python or tool as 'value'."})
                return await self.decide_execution(correction_prompt)

    def submit_text(self) -> None:
        user_input = self.input_text_area.get("1.0", "end-1c")
        if not user_input.strip():
            return
        full_prompt = self.build_full_prompt(user_input)
        self.submit_button.config(state=tk.DISABLED)
        self.text_prompt.append({'role': 'user', 'content': full_prompt})
        self.update_user_input_history()
        # Clear both output and scratchpad areas
        self.output_text_area.delete("1.0", tk.END)
        self.scratchpad_text_area.delete("1.0", tk.END)

        def run_mode_inference():
            mode = self.mode_var.get().lower()
            response = ""
            try:
                # Create a dual widget that sends updates to both final output and scratchpad.
                dual_widget = DualTextWidget(
                    self.output_text_area, self.scratchpad_text_area)
                if mode == "tool":
                    result_tuple = asyncio.run(self.tool_use(self.text_prompt))
                    response = "".join(result_tuple[0]) if isinstance(
                        result_tuple[0], list) else result_tuple[0]
                    self.text_prompt.append(
                        {'role': 'assistant', 'content': response})
                elif mode == "code":
                    result_tuple = asyncio.run(self.code_use(self.text_prompt))
                    response = "".join(result_tuple[0]) if isinstance(
                        result_tuple[0], list) else result_tuple[0]
                    self.text_prompt.append(
                        {'role': 'assistant', 'content': response})
                elif mode == "auto":
                    response = asyncio.run(
                        self.decide_execution(self.text_prompt))
                    self.text_prompt.append(
                        {'role': 'assistant', 'content': response})
                else:
                    response = run_inference(
                        self.text_prompt, dual_widget, self.root, self.model_var.get())
                    self.text_prompt.append(
                        {'role': 'assistant', 'content': response})
                self.update_assistant_response_history()

                # If the response is valid, add it to the vector DB:
                if response and "Error" not in response:
                    from simple.code.memory import add_response_to_db
                    # Create a unique response ID using current timestamp.
                    response_id = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    add_response_to_db(response, response_id)

            except Exception as e:
                logging.error(f"Error during inference: {e}")
            finally:
                self.input_text_area.delete("1.0", tk.END)
                self.submit_button.config(state=tk.NORMAL)
                self.history_manager.save_history(self.text_prompt)

        threading.Thread(target=run_mode_inference).start()

    def update_system_prompt(self) -> None:
        new_prompt = self.system_text_area.get("1.0", "end-1c")
        if new_prompt.strip():
            self.text_prompt[0]['content'] = new_prompt
            self.history_manager.save_history(self.text_prompt)

    def show_previous_input(self) -> None:
        if not self.user_input_history:
            return
        if self.user_input_history_index is None:
            self.user_input_history_index = len(self.user_input_history) - 1
        elif self.user_input_history_index > 0:
            self.user_input_history_index -= 1
        self.input_text_area.delete("1.0", tk.END)
        self.input_text_area.insert(
            "1.0", self.user_input_history[self.user_input_history_index])

    def show_next_input(self) -> None:
        if not self.user_input_history or self.user_input_history_index is None:
            return
        if self.user_input_history_index < len(self.user_input_history) - 1:
            self.user_input_history_index += 1
            self.input_text_area.delete("1.0", tk.END)
            self.input_text_area.insert(
                "1.0", self.user_input_history[self.user_input_history_index])
        else:
            self.user_input_history_index = None
            self.input_text_area.delete("1.0", tk.END)

    def show_previous_response(self) -> None:
        if not self.assistant_response_history:
            return
        if self.assistant_response_history_index is None:
            self.assistant_response_history_index = len(
                self.assistant_response_history) - 1
        elif self.assistant_response_history_index > 0:
            self.assistant_response_history_index -= 1
        self.output_text_area.delete("1.0", tk.END)
        self.output_text_area.insert(
            "1.0", self.assistant_response_history[self.assistant_response_history_index])

    def show_next_response(self) -> None:
        if not self.assistant_response_history or self.assistant_response_history_index is None:
            return
        if self.assistant_response_history_index < len(self.assistant_response_history) - 1:
            self.assistant_response_history_index += 1
            self.output_text_area.delete("1.0", tk.END)
            self.output_text_area.insert(
                "1.0", self.assistant_response_history[self.assistant_response_history_index])
        else:
            self.assistant_response_history_index = None
            self.output_text_area.delete("1.0", tk.END)

    def clear_conversation(self) -> None:
        system_prompt = self.text_prompt[0]
        self.text_prompt = [system_prompt]
        self.user_input_history = []
        self.assistant_response_history = []
        self.input_text_area.delete("1.0", tk.END)
        self.output_text_area.delete("1.0", tk.END)
        self.scratchpad_text_area.delete("1.0", tk.END)
        self.history_manager.save_history(self.text_prompt)
        logging.info("Conversation cleared.")

    def extract_code_snippets(self) -> None:
        language = self.code_language_var.get()
        output_text = self.output_text_area.get("1.0", "end-1c")
        snippets = self.extract_code_blocks(output_text, language)
        extract_window = tk.Toplevel(self.root)
        extract_window.title(
            f"Extracted {language.capitalize()} Code Snippets")
        if not snippets:
            tk.Label(extract_window, text=f"No code snippets found for language: {language}").pack(
                padx=5, pady=5)
            return
        snippet_listbox = tk.Listbox(extract_window)
        snippet_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        for idx in range(1, len(snippets) + 1):
            snippet_listbox.insert(tk.END, f"Snippet {idx}")
        preview_text = tk.Text(extract_window, height=10)
        preview_text.pack(fill="both", expand=True, padx=5, pady=5)

        def on_select(evt):
            widget = evt.widget
            if not widget.curselection():
                return
            index = int(widget.curselection()[0])
            preview_text.delete("1.0", tk.END)
            preview_text.insert(tk.END, snippets[index])
        snippet_listbox.bind("<<ListboxSelect>>", on_select)

        def save_selected_snippet():
            selection = snippet_listbox.curselection()
            if not selection:
                logging.info("No snippet selected.")
                return
            index = int(selection[0])
            snippet = snippets[index]
            file_path = filedialog.asksaveasfilename(title="Save Snippet", defaultextension=".py",
                                                     filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(snippet)
                    logging.info(f"Snippet saved to {file_path}")
                except Exception as e:
                    logging.error(f"Error saving snippet: {e}")
        tk.Button(extract_window, text="Save Selected Snippet",
                  command=save_selected_snippet).pack(pady=5)

        if language.lower() == "python":
            def execute_selected_snippet():
                selection = snippet_listbox.curselection()
                if not selection:
                    logging.info("No snippet selected.")
                    return
                index = int(selection[0])
                snippet = snippets[index]

                def run_code():
                    output_capture = io.StringIO()
                    try:
                        with contextlib.redirect_stdout(output_capture), contextlib.redirect_stderr(output_capture):
                            exec(snippet, {})
                    except Exception as e:
                        output_capture.write(f"Error executing code: {e}")
                    result = output_capture.getvalue()
                    output_capture.close()
                    result_window = tk.Toplevel(extract_window)
                    result_window.title("Execution Result")
                    result_text = tk.Text(result_window, wrap="none")
                    result_text.pack(fill="both", expand=True)
                    result_text.insert("1.0", result)

                    def send_to_input():
                        main_input = result_text.get("1.0", "end-1c")
                        self.input_text_area.delete("1.0", tk.END)
                        self.input_text_area.insert("1.0", main_input)
                    tk.Button(result_window, text="Send to Input",
                              command=send_to_input).pack(pady=5)
                threading.Thread(target=run_code).start()
            tk.Button(extract_window, text="Execute Selected Snippet",
                      command=execute_selected_snippet).pack(pady=5)

    def extract_suggested_files(self, text: str) -> list:
        pattern = rf"{MD_HEADING}\s*(.*?)\s*:\s*\n```(?:python)?\n(.*?)```"
        return re.findall(pattern, text, re.DOTALL)

    def save_suggested_files_from_output(self) -> None:
        text = self.output_text_area.get("1.0", "end-1c")
        files = self.extract_suggested_files(text)
        if not files:
            logging.info("No suggested files found in output.")
            return
        base_dir = self.codebase_path_entry.get().strip() or "suggested_files"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        for filename, code in files:
            full_path = os.path.join(base_dir, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(code)
                logging.info(f"Saved {full_path}")
            except Exception as e:
                logging.error(f"Error saving {full_path}: {e}")

    def ensure_default_system_prompt(self) -> None:
        folder = "gag/system_prompts"
        if not os.path.exists(folder):
            os.makedirs(folder)
        default_file = os.path.join(folder, "flexi.txt")
        default_prompt = "You are Flexi💻AI. You think step by step, keeping key points in mind to solve or answer the request."
        if not os.path.exists(default_file):
            with open(default_file, "w", encoding="utf-8") as f:
                f.write(default_prompt)

    def get_system_prompt_files(self) -> list:
        folder = "gag/system_prompts"
        self.ensure_default_system_prompt()
        return [f for f in os.listdir(folder) if f.endswith(".txt")]

    def update_system_prompts_dropdown(self) -> None:
        files = self.get_system_prompt_files()
        menu = self.system_prompt_dropdown["menu"]
        menu.delete(0, "end")
        if files:
            self.system_prompt_var.set(files[0])
            for file in files:
                menu.add_command(
                    label=file, command=lambda value=file: self.system_prompt_var.set(value))
        else:
            self.system_prompt_var.set("flexi.txt")
            menu.add_command(label="flexi.txt", command=lambda: None)

    def load_system_prompt_file(self) -> None:
        file_name = self.system_prompt_var.get()
        file_path = os.path.join("gag/system_prompts", file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.system_text_area.delete("1.0", tk.END)
            self.system_text_area.insert("1.0", content)
            self.text_prompt[0]["content"] = content
        except Exception as e:
            logging.error(f"Error loading system prompt: {e}")

    def save_system_prompt_as_new(self) -> None:
        prompt_name = self.prompt_name_entry.get().strip()
        if not prompt_name:
            prompt_name = f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        elif not prompt_name.endswith(".txt"):
            prompt_name += ".txt"
        file_path = os.path.join("gag/system_prompts", prompt_name)
        content = self.system_text_area.get("1.0", "end-1c")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info(f"System prompt saved as {file_path}")
        except Exception as e:
            logging.error(f"Error saving system prompt: {e}")
        self.update_system_prompts_dropdown()

    def delete_system_prompt_file(self) -> None:
        file_name = self.system_prompt_var.get()
        if file_name == "flexi.txt":
            logging.info("Cannot delete the default system prompt.")
            return
        file_path = os.path.join("gag/system_prompts", file_name)
        try:
            os.remove(file_path)
            logging.info(f"Deleted system prompt: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting system prompt: {e}")
        self.update_system_prompts_dropdown()

    def load_history(self) -> None:
        selected_file = self.history_var.get()
        history_path = os.path.join(
            self.history_manager.history_dir, selected_file)
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                loaded_history = json.load(f)
            self.text_prompt = loaded_history
            self.current_history_file = selected_file
            if self.text_prompt and self.text_prompt[0].get("role") == "system":
                self.system_text_area.delete("1.0", tk.END)
                self.system_text_area.insert(
                    "1.0", self.text_prompt[0]["content"])
            self.update_user_input_history()
            self.update_assistant_response_history()
        except Exception as e:
            logging.error(f"Error loading history file: {e}")

    def save_history(self) -> None:
        history_dir = self.history_manager.history_dir
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
        file_name = self.history_filename_entry.get().strip()
        if not file_name:
            if not self.current_history_file:
                file_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                file_name = self.current_history_file
        elif not file_name.endswith(".json"):
            file_name += ".json"
        self.current_history_file = file_name
        history_path = os.path.join(history_dir, file_name)
        try:
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(self.text_prompt, f, indent=4)
            logging.info(f"History saved to {history_path}")
            return history_path
        except Exception as e:
            logging.error(f"Error saving history: {e}")
            return None
        self.update_history_dropdown()

    def auto_save_history(self) -> None:
        history_dir = self.history_manager.history_dir
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
        if not self.current_history_file:
            file_name = self.history_filename_entry.get().strip()
            if not file_name:
                file_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            elif not file_name.endswith(".json"):
                file_name += ".json"
            self.current_history_file = file_name
        history_path = os.path.join(history_dir, self.current_history_file)
        try:
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(self.text_prompt, f, indent=4)
            logging.info(f"History automatically saved to {history_path}")
        except Exception as e:
            logging.error(f"Error auto-saving history: {e}")
        self.update_history_dropdown()

    def update_history_dropdown(self) -> None:
        history_files = self.history_manager.get_history_files()
        menu = self.history_dropdown["menu"]
        menu.delete(0, "end")
        if history_files:
            self.history_var.set(history_files[0])
            for file in history_files:
                menu.add_command(
                    label=file, command=lambda value=file: self.history_var.set(value))
        else:
            self.history_var.set("No history files")
            menu.add_command(label="No history files", command=lambda: None)

    def delete_history(self) -> None:
        selected_file = self.history_var.get()
        if selected_file == "No history files":
            logging.info("No history file selected to delete.")
            return
        history_path = os.path.join(
            self.history_manager.history_dir, selected_file)
        try:
            os.remove(history_path)
            logging.info(f"Deleted history file: {history_path}")
            self.update_history_dropdown()
        except Exception as e:
            logging.error(f"Error deleting history file: {e}")

    def view_history(self) -> None:
        selected_file = self.history_var.get()
        if selected_file == "No history files":
            logging.info("No history file selected to view.")
            return
        history_path = os.path.join(
            self.history_manager.history_dir, selected_file)
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logging.error(f"Error reading history file: {e}")
            return
        view_window = tk.Toplevel(self.root)
        view_window.title(f"View History: {selected_file}")
        text_widget = tk.Text(view_window, wrap="none")
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(view_window, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.insert("1.0", content)


def execute_python_code(code: str) -> dict:
    """
    Executes a string of Python code in a separate process.
    Writes the code to a temporary file and runs it via the system Python interpreter.
    Returns:
        Dict[str, str]: A dictionary with "status" and "message".
    """
    result = {"status": "", "message": ""}
    temp_filename = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as temp_file:
            temp_file.write(code)
            temp_filename = temp_file.name
        process = subprocess.Popen(
            ["python", temp_filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            result['status'] = "500"
            result[
                'message'] = f"Execution failed with exit code {process.returncode}:\n{stderr.decode('utf-8')}"
        else:
            result['status'] = "200"
            result['message'] = "Execution successful\nResult:\n" + \
                stdout.decode('utf-8')
    except Exception as e:
        result['status'] = "500"
        result['message'] = f"Execution failed:\n{str(e)}"
    finally:
        if temp_filename and os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception:
                pass
    return result




def main() -> None:
    root = tk.Tk()
    app = FlexiAIApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
