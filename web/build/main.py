import os
import shutil  # Needed for directory removal
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox


def load_projects(projects_dir):
    """
    Reads project directories from the given folder.
    Returns a list of tuples: (project_name, status, deployable).
    For this example, we set default values for status and deployable.
    """
    projects_list = []
    if os.path.isdir(projects_dir):
        for entry in os.listdir(projects_dir):
            path = os.path.join(projects_dir, entry)
            if os.path.isdir(path):
                status = "Active"
                deployable = "Yes"
                projects_list.append((entry, status, deployable))
    else:
        print(f"Directory {projects_dir} not found.")
    return projects_list


def delete_project():
    """Deletes the selected project from both the UI and filesystem."""
    selected_item = projects_tree.selection()
    if not selected_item:
        messagebox.showwarning(
            "No Selection", "Please select a project to delete.")
        return

    confirm = messagebox.askyesno(
        "Confirm Deletion", "Are you sure you want to delete the selected project?")
    if not confirm:
        return

    # Get project name from the selected Treeview item
    project_values = projects_tree.item(selected_item, "values")
    project_name = project_values[0]

    # Build the full path to the project directory
    project_path = os.path.join(projects_dir, project_name)

    try:
        shutil.rmtree(project_path)
    except Exception as e:
        messagebox.showerror(
            "Error", f"Failed to delete project directory:\n{e}")
        return

    # Remove the project from the Treeview
    projects_tree.delete(selected_item)
    messagebox.showinfo(
        "Deleted", f"Project '{project_name}' has been deleted.")


def run_interactive_command(cmd):
    """
    Opens a new Toplevel window that runs an interactive command.
    The process output is displayed in a Text widget,
    and user input is sent to the process via an Entry widget.
    """
    win = tk.Toplevel(root)
    win.title("Interactive Command")
    win.geometry("600x400")

    output_text = tk.Text(win, height=20, width=80)
    output_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    input_frame = ttk.Frame(win)
    input_frame.pack(fill=tk.X, padx=10, pady=5)
    input_entry = ttk.Entry(input_frame)
    input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    send_button = ttk.Button(input_frame, text="Send")
    send_button.pack(side=tk.RIGHT)

    # Debug: print the command we're about to run
    print("Running command:", cmd)

    try:
        # First, try without shell
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                bufsize=1)
    except FileNotFoundError as e:
        # If it fails, try using shell=True (and join the cmd into a string)
        print("Command not found; trying with shell=True")
        cmd_str = " ".join(cmd)
        proc = subprocess.Popen(cmd_str,
                                stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                shell=True,
                                bufsize=1)

    output_queue = queue.Queue()

    def read_output():
        for line in proc.stdout:
            output_queue.put(line)
        proc.stdout.close()

    def update_output():
        try:
            while True:
                line = output_queue.get_nowait()
                output_text.insert(tk.END, line)
                output_text.see(tk.END)
        except queue.Empty:
            pass
        if proc.poll() is None:
            win.after(100, update_output)
        else:
            output_text.insert(tk.END, "\nProcess finished.\n")
    threading.Thread(target=read_output, daemon=True).start()
    update_output()

    def send_input():
        user_input = input_entry.get() + "\n"
        try:
            proc.stdin.write(user_input)
            proc.stdin.flush()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send input: {e}")
        input_entry.delete(0, tk.END)

    send_button.config(command=send_input)


def create_nextjs_project():
    """Prompts for a project name and creates a new Next.js application interactively."""
    project_name = simpledialog.askstring(
        "Create New Project", "Enter new project name:")
    if not project_name:
        return

    # Define the projects directory (./web/site) relative to this script
    global projects_dir
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)

    project_path = os.path.join(projects_dir, project_name)
    if os.path.exists(project_path):
        messagebox.showerror(
            "Error", f"Project '{project_name}' already exists.")
        return

    # Debug: print the project path that will be created
    print("Creating project at:", project_path)

    cmd = ["npx.cmd", "create-next-app", project_path]
    run_interactive_command(cmd)
    projects_tree.insert("", tk.END, values=(project_name, "Active", "Yes"))


# Create the main application window
root = tk.Tk()
root.title("Website Management Dashboard")
root.geometry("900x600")

# Create a Notebook (tabs container)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# -----------------------
# Dashboard Tab
# -----------------------
dashboard_frame = ttk.Frame(notebook)
notebook.add(dashboard_frame, text="Dashboard")
dashboard_title = ttk.Label(
    dashboard_frame, text="Projects Analytics Dashboard", font=("Helvetica", 16))
dashboard_title.pack(pady=10)
metrics_frame = ttk.Frame(dashboard_frame)
metrics_frame.pack(pady=20)
visitors_frame = ttk.LabelFrame(metrics_frame, text="Visitors", padding=10)
visitors_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
ttk.Label(visitors_frame, text="Total Visitors: 12,345").pack()
ttk.Label(visitors_frame, text="Unique Visitors: 6,789").pack()
interactions_frame = ttk.LabelFrame(
    metrics_frame, text="Interactions", padding=10)
interactions_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
ttk.Label(interactions_frame, text="Clicks: 2,345").pack()
ttk.Label(interactions_frame, text="Comments: 123").pack()
location_frame = ttk.LabelFrame(metrics_frame, text="Location", padding=10)
location_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
ttk.Label(location_frame, text="Top Countries: USA, UK, Canada").pack()
device_frame = ttk.LabelFrame(metrics_frame, text="Device Type", padding=10)
device_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
ttk.Label(device_frame, text="Desktop: 60%").pack()
ttk.Label(device_frame, text="Mobile: 40%").pack()

# -----------------------
# Projects CRUD Tab
# -----------------------
projects_frame = ttk.Frame(notebook)
notebook.add(projects_frame, text="Projects")
projects_title = ttk.Label(
    projects_frame, text="Projects Management", font=("Helvetica", 16))
projects_title.pack(pady=10)
proj_columns = ("Name", "Status", "Deployable")
projects_tree = ttk.Treeview(
    projects_frame, columns=proj_columns, show="headings", height=10)
for col in proj_columns:
    projects_tree.heading(col, text=col)
    projects_tree.column(col, width=200)
projects_tree.pack(pady=10, padx=10, fill='x')

# Set global projects_dir for reuse in functions
projects_dir = os.path.join(os.path.dirname(__file__), "web", "site")
for proj in load_projects(projects_dir):
    projects_tree.insert("", tk.END, values=proj)

proj_buttons_frame = ttk.Frame(projects_frame)
proj_buttons_frame.pack(pady=10)
ttk.Button(proj_buttons_frame, text="View Project").grid(
    row=0, column=0, padx=5)
ttk.Button(proj_buttons_frame, text="Create New Project",
           command=create_nextjs_project).grid(row=0, column=1, padx=5)
ttk.Button(proj_buttons_frame, text="Delete Project",
           command=delete_project).grid(row=0, column=2, padx=5)
ttk.Button(proj_buttons_frame, text="Set as Deployable").grid(
    row=0, column=3, padx=5)
ttk.Button(proj_buttons_frame, text="Edit Project").grid(
    row=0, column=4, padx=5)

# -----------------------
# Deployments CRUD Tab
# -----------------------
deployments_frame = ttk.Frame(notebook)
notebook.add(deployments_frame, text="Deployments")
deployments_title = ttk.Label(
    deployments_frame, text="Project Deployments", font=("Helvetica", 16))
deployments_title.pack(pady=10)
dep_columns = ("Name", "Date Deployed", "Status")
deployments_tree = ttk.Treeview(
    deployments_frame, columns=dep_columns, show="headings", height=10)
for col in dep_columns:
    deployments_tree.heading(col, text=col)
    deployments_tree.column(col, width=200)
deployments_tree.pack(pady=10, padx=10, fill='x')
for dep in [("Project A", "2025-01-01", "Live"), ("Project B", "2025-01-05", "Offline")]:
    deployments_tree.insert("", tk.END, values=dep)
deploy_buttons_frame = ttk.Frame(deployments_frame)
deploy_buttons_frame.pack(pady=10)
ttk.Button(deploy_buttons_frame, text="View Deployed Project").grid(
    row=0, column=0, padx=5)
ttk.Button(deploy_buttons_frame, text="Download Deployment").grid(
    row=0, column=1, padx=5)
ttk.Button(deploy_buttons_frame, text="Create New Deployment").grid(
    row=0, column=2, padx=5)
ttk.Button(deploy_buttons_frame, text="Delete Deployment").grid(
    row=0, column=3, padx=5)

root.mainloop()
