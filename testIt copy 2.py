import tkinter as tk
from tkinter.scrolledtext import ScrolledText


class FlexiAgentApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Two Text Areas Side by Side")

        # Create a frame to hold the two text areas
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        # Directory and tips frame for agent context
        # # Right text area with a scrollbar
        right_frame = tk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(0, 5))
        right_text = ScrolledText(
            right_frame, wrap=tk.WORD, width=40, height=10)
        right_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
       

        # Directory and tips frame for agent context
        left_frame = tk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH,
                             expand=True, pady=(0, 5))
        tk.Label(left_frame, text="Agent Work Directory:").grid(
            row=0, column=0, sticky="w")
        self.codebase_path_entry = tk.Entry(left_frame)
        self.codebase_path_entry.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Label(left_frame, text="Additional Tips:").grid(
            row=1, column=0, sticky="w")
        self.tips_entry = tk.Text(left_frame, height=3)
        self.tips_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

def main() -> None:
    root = tk.Tk()
    app = FlexiAgentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
