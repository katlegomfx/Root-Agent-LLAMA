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

from simple import utils
from simple.inference import run_inference
from simple.history import HistoryManager
from simple.system_prompts import SystemPromptManager

# At the top of gui.py (after imports and before other functions)
from simple.inference import current_client  # used to access the global client


def cancel_inference():
    try:
        # Import the global current_client from inference.
        from simple.inference import current_client
        if current_client:
            current_client.cancel()
            print("Inference cancellation requested.")
        else:
            print("No active inference to cancel.")
    except Exception as e:
        print(f"Error cancelling inference: {e}")

# ... (rest of the file)




# Global conversation prompt
text_prompt = [
    {
        'role': 'system',
        'content': "You are Flexi💻AI. You think step by step, keeping key points in mind to solve or answer the request."
    }
]

model_map = {
    'llama3.2': ()
}

# Global history lists
user_input_history = []
user_input_history_index = None
assistant_response_history = []
assistant_response_history_index = None


def update_user_input_history():
    global user_input_history, user_input_history_index
    user_input_history = [msg["content"]
                          for msg in text_prompt if msg.get("role") == "user"]
    user_input_history_index = None


def update_assistant_response_history():
    global assistant_response_history, assistant_response_history_index
    assistant_response_history = [msg["content"]
                                  for msg in text_prompt if msg.get("role") == "assistant"]
    assistant_response_history_index = None


def build_full_prompt(user_request: str) -> str:
    codebase_path = codebase_path_entry.get().strip()
    base_code = ""
    if codebase_path:
        try:
            base_code_list = utils.code_corpus(codebase_path)
            base_code = "\n".join(base_code_list)
        except Exception as e:
            print(f"Error reading codebase: {e}")
    tips = tips_entry.get("1.0", "end-1c").strip()
    full_prompt = f"#### Codebase:\n\n{base_code}\n\n#### {user_request}\n\n{tips}"
    return full_prompt


def submit_text():
    global user_input_history, user_input_history_index, submit_button
    user_input = input_text_area.get("1.0", "end-1c")
    if user_input.strip() == "":
        return
    full_prompt = build_full_prompt(user_input)
    submit_button.config(state=tk.DISABLED)
    text_prompt.append({'role': 'user', 'content': full_prompt})
    update_user_input_history()
    output_text_area.delete("1.0", tk.END)

    def run_inference_thread():
        response = run_inference(
            text_prompt, output_text_area, root, model_var.get())
        text_prompt.append({'role': 'assistant', 'content': response})
        update_assistant_response_history()
        input_text_area.delete("1.0", "end")
        submit_button.config(state=tk.NORMAL)
        history_manager.save_history(text_prompt)
    threading.Thread(target=run_inference_thread).start()


def update_system_prompt():
    new_prompt = system_text_area.get("1.0", "end-1c")
    if new_prompt.strip() != "":
        text_prompt[0]['content'] = new_prompt
        history_manager.save_history(text_prompt)


def show_previous_input():
    global user_input_history, user_input_history_index
    if not user_input_history:
        return
    if user_input_history_index is None:
        user_input_history_index = len(user_input_history) - 1
    elif user_input_history_index > 0:
        user_input_history_index -= 1
    input_text_area.delete("1.0", tk.END)
    input_text_area.insert("1.0", user_input_history[user_input_history_index])


def show_next_input():
    global user_input_history, user_input_history_index
    if not user_input_history or user_input_history_index is None:
        return
    if user_input_history_index < len(user_input_history) - 1:
        user_input_history_index += 1
        input_text_area.delete("1.0", tk.END)
        input_text_area.insert(
            "1.0", user_input_history[user_input_history_index])
    else:
        user_input_history_index = None
        input_text_area.delete("1.0", tk.END)


def show_previous_response():
    global assistant_response_history, assistant_response_history_index
    if not assistant_response_history:
        return
    if assistant_response_history_index is None:
        assistant_response_history_index = len(assistant_response_history) - 1
    elif assistant_response_history_index > 0:
        assistant_response_history_index -= 1
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert(
        "1.0", assistant_response_history[assistant_response_history_index])


def show_next_response():
    global assistant_response_history, assistant_response_history_index
    if not assistant_response_history or assistant_response_history_index is None:
        return
    if assistant_response_history_index < len(assistant_response_history) - 1:
        assistant_response_history_index += 1
        output_text_area.delete("1.0", tk.END)
        output_text_area.insert(
            "1.0", assistant_response_history[assistant_response_history_index])
    else:
        assistant_response_history_index = None
        output_text_area.delete("1.0", tk.END)


def clear_conversation():
    global text_prompt, user_input_history, assistant_response_history
    system_prompt = text_prompt[0]
    text_prompt = [system_prompt]
    user_input_history = []
    assistant_response_history = []
    input_text_area.delete("1.0", tk.END)
    output_text_area.delete("1.0", tk.END)
    history_manager.save_history(text_prompt)
    print("Conversation cleared.")


def extract_code_snippets():
    language = code_language_var.get()
    output_text = output_text_area.get("1.0", "end-1c")
    pattern = r"```" + re.escape(language) + r"\s*\n(.*?)```"
    snippets = re.findall(pattern, output_text, re.DOTALL)
    extract_window = tk.Toplevel(root)
    extract_window.title(f"Extracted {language.capitalize()} Code Snippets")
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
        w = evt.widget
        if not w.curselection():
            return
        index = int(w.curselection()[0])
        preview_text.delete("1.0", tk.END)
        preview_text.insert(tk.END, snippets[index])
    snippet_listbox.bind("<<ListboxSelect>>", on_select)

    def save_selected_snippet():
        selection = snippet_listbox.curselection()
        if not selection:
            print("No snippet selected.")
            return
        index = int(selection[0])
        snippet = snippets[index]
        file_path = filedialog.asksaveasfilename(title="Save Snippet", defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(snippet)
            print(f"Snippet saved to {file_path}")
    save_snippet_button = tk.Button(
        extract_window, text="Save Selected Snippet", command=save_selected_snippet)
    save_snippet_button.pack(pady=5)

    if language.lower() == "python":
        def execute_selected_snippet():
            selection = snippet_listbox.curselection()
            if not selection:
                print("No snippet selected.")
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
                    input_text_area.delete("1.0", "end")
                    input_text_area.insert("1.0", main_input)
                send_button = tk.Button(
                    result_window, text="Send to Input", command=send_to_input)
                send_button.pack(pady=5)
            threading.Thread(target=run_code).start()
        execute_snippet_button = tk.Button(
            extract_window, text="Execute Selected Snippet", command=execute_selected_snippet)
        execute_snippet_button.pack(pady=5)


def extract_suggested_files(text: str):
    pattern = r"###\s*(.*?)\s*:\s*\n```(?:python)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def save_suggested_files_from_output():
    text = output_text_area.get("1.0", "end-1c")
    files = extract_suggested_files(text)
    if not files:
        print("No suggested files found in output.")
        return
    base_dir = codebase_path_entry.get().strip()
    if base_dir == "":
        base_dir = "suggested_files"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    for filename, code in files:
        full_path = os.path.join(base_dir, filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"Saved {full_path}")
        except Exception as e:
            print(f"Error saving {full_path}: {e}")


# Initialize managers
history_manager = HistoryManager()
prompt_manager = SystemPromptManager()

# Build the main window
root = tk.Tk()
root.title("Flexi💻AI")
root.geometry("600x1000")

# --- Model Selection Section ---
model_frame = tk.Frame(root)
model_frame.pack(fill="x", padx=5, pady=5)
model_label = tk.Label(model_frame, text="Select Model:")
model_label.grid(row=0, column=0, sticky="w")
model_options = list(model_map.keys()) if model_map else ["llama3.2"]
model_var = tk.StringVar(model_frame)
model_var.set(model_options[0])
model_dropdown = tk.OptionMenu(model_frame, model_var, *model_options)
model_dropdown.grid(row=0, column=1, padx=5, pady=5)

# --- System Prompt Section ---
system_frame = tk.Frame(root)
system_frame.pack(fill="x", padx=5, pady=5)
system_label = tk.Label(system_frame, text="System Prompt:")
system_label.grid(row=0, column=0, sticky="w")
system_text_area = tk.Text(system_frame, height=3)
system_text_area.grid(row=1, column=0, sticky="ew", padx=(0, 5))
system_text_area.insert("1.0", text_prompt[0]["content"])
update_system_button = tk.Button(
    system_frame, text="Update System Prompt", command=update_system_prompt)
update_system_button.grid(row=1, column=1, sticky="e")
system_frame.grid_columnconfigure(0, weight=1)

# --- System Prompt Management Section ---
system_prompt_mgmt_frame = tk.Frame(root)
system_prompt_mgmt_frame.pack(fill="x", padx=5, pady=5)
system_prompt_label = tk.Label(
    system_prompt_mgmt_frame, text="System Prompts:")
system_prompt_label.grid(row=0, column=0, sticky="w")
system_prompt_var = tk.StringVar(system_prompt_mgmt_frame)
system_prompt_dropdown = tk.OptionMenu(
    system_prompt_mgmt_frame, system_prompt_var, "")
system_prompt_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
load_prompt_button = tk.Button(
    system_prompt_mgmt_frame, text="Load Prompt", command=load_system_prompt_file)
load_prompt_button.grid(row=0, column=2, padx=5, pady=5)
prompt_name_label = tk.Label(system_prompt_mgmt_frame, text="Prompt Name:")
prompt_name_label.grid(row=1, column=0, sticky="w")
prompt_name_entry = tk.Entry(system_prompt_mgmt_frame)
prompt_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
save_prompt_button = tk.Button(
    system_prompt_mgmt_frame, text="Save as New", command=save_system_prompt_as_new)
save_prompt_button.grid(row=1, column=2, padx=5, pady=5)
delete_prompt_button = tk.Button(
    system_prompt_mgmt_frame, text="Delete Prompt", command=delete_system_prompt_file)
delete_prompt_button.grid(row=1, column=3, padx=5, pady=5)
system_prompt_mgmt_frame.grid_columnconfigure(1, weight=1)
update_system_prompts_dropdown()

# --- History Section ---
history_frame = tk.Frame(root)
history_frame.pack(fill="x", padx=5, pady=5)
history_label = tk.Label(history_frame, text="History Files:")
history_label.grid(row=0, column=0, sticky="w")
history_var = tk.StringVar(history_frame)
history_files = history_manager.get_history_files()
if history_files:
    history_var.set(history_files[0])
    history_dropdown = tk.OptionMenu(
        history_frame, history_var, *history_files)
else:
    history_var.set("No history files")
    history_dropdown = tk.OptionMenu(
        history_frame, history_var, "No history files")
history_dropdown.grid(row=0, column=1, padx=5, pady=5)
load_history_button = tk.Button(
    history_frame, text="Load History", command=lambda: load_history())
load_history_button.grid(row=0, column=2, padx=5, pady=5)
delete_history_button = tk.Button(history_frame, text="Delete History",
                                  command=lambda: history_manager.delete_history(history_var.get()))
delete_history_button.grid(row=0, column=3, padx=5, pady=5)
view_history_button = tk.Button(
    history_frame, text="View History", command=view_history)
view_history_button.grid(row=0, column=4, padx=5, pady=5)
history_filename_label = tk.Label(history_frame, text="File Name:")
history_filename_label.grid(row=1, column=0, sticky="w", pady=5)
history_filename_entry = tk.Entry(history_frame)
history_filename_entry.grid(row=1, column=1, padx=5, pady=5)
save_history_button = tk.Button(history_frame, text="Save History", command=lambda: history_manager.save_history(
    text_prompt, history_filename_entry.get()))
save_history_button.grid(row=1, column=2, padx=5, pady=5)
history_frame.grid_columnconfigure(0, weight=1)

# --- Code Append Section ---
code_append_frame = tk.Frame(root)
code_append_frame.pack(fill="x", padx=5, pady=5)
codebase_label = tk.Label(code_append_frame, text="Codebase Directory:")
codebase_label.grid(row=0, column=0, sticky="w")
codebase_path_entry = tk.Entry(code_append_frame)
codebase_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
tips_label = tk.Label(code_append_frame, text="Additional Tips:")
tips_label.grid(row=1, column=0, sticky="w")
tips_entry = tk.Text(code_append_frame, height=3)
tips_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
code_append_frame.grid_columnconfigure(1, weight=1)

# --- Input Section for User Prompts ---
input_frame = tk.Frame(root)
input_frame.pack(fill="x", padx=5, pady=5)
input_text_area = tk.Text(input_frame, height=5)
input_text_area.grid(row=0, column=0, sticky="ew", padx=(0, 5))
control_frame = tk.Frame(input_frame)
control_frame.grid(row=0, column=1, sticky="ns")
up_arrow_button = tk.Button(control_frame, text="↑",
                            command=show_previous_input)
up_arrow_button.pack(fill="x")
submit_button = tk.Button(control_frame, text="Submit", command=submit_text)
submit_button.pack(fill="x")
down_arrow_button = tk.Button(control_frame, text="↓", command=show_next_input)
down_arrow_button.pack(fill="x")
# New Cancel button:
cancel_button = tk.Button(control_frame, text="Cancel",
                          command=cancel_inference)
cancel_button.pack(fill="x", pady=5)
clear_button = tk.Button(
    control_frame, text="Clear Conversation", command=clear_conversation)
clear_button.pack(fill="x", pady=5)
input_frame.grid_columnconfigure(0, weight=1)


# --- Output Section for Inference Results ---
output_frame = tk.Frame(root)
output_frame.pack(fill="both", expand=True, padx=5, pady=5)
response_control_frame = tk.Frame(output_frame)
response_control_frame.pack(fill="x")
prev_response_button = tk.Button(
    response_control_frame, text="Assistant ↑", command=show_previous_response)
prev_response_button.pack(side="left", padx=5, pady=2)
next_response_button = tk.Button(
    response_control_frame, text="Assistant ↓", command=show_next_response)
next_response_button.pack(side="left", padx=5, pady=2)
output_scrollbar = tk.Scrollbar(output_frame)
output_scrollbar.pack(side="right", fill="y")
output_text_area = tk.Text(output_frame, yscrollcommand=output_scrollbar.set)
output_text_area.pack(fill="both", expand=True)
output_scrollbar.config(command=output_text_area.yview)

# --- Code Extraction Section ---
code_extraction_frame = tk.Frame(root)
code_extraction_frame.pack(fill="x", padx=5, pady=5)
code_language_label = tk.Label(
    code_extraction_frame, text="Extract Code Snippets (Language):")
code_language_label.grid(row=0, column=0, sticky="w")
code_language_var = tk.StringVar(code_extraction_frame)
code_language_var.set("python")
code_language_dropdown = tk.OptionMenu(
    code_extraction_frame, code_language_var, "python", "bash", "json")
code_language_dropdown.grid(row=0, column=1, padx=5, pady=5)
extract_code_button = tk.Button(
    code_extraction_frame, text="Extract Code", command=extract_code_snippets)
extract_code_button.grid(row=0, column=2, padx=5, pady=5)
save_suggested_files_button = tk.Button(
    code_extraction_frame, text="Save Suggested Files", command=save_suggested_files_from_output)
save_suggested_files_button.grid(row=0, column=3, padx=5, pady=5)
code_extraction_frame.grid_columnconfigure(0, weight=1)


def main():
    root.mainloop()


if __name__ == '__main__':
    main()
