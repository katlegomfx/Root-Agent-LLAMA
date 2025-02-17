# Bot\build\code\gui\gui_application.py
# ./Bot/build/code/gui/gui_application.py
import asyncio
import tkinter as tk
from threading import Thread, Event

class GUIApplication:
    """
    A simple Tkinter-based GUI that invokes methods from CLIApplication in the background.
    """

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.root = tk.Tk()
        self.root.title("Flexi GUI")

        # A place to display user input
        self.input_box = tk.Entry(self.root, width=60)
        self.input_box.pack(pady=10)

        # Submit button
        self.submit_button = tk.Button(
            self.root, text="Send", command=self.on_submit)
        self.submit_button.pack()

        # Output area (readonly text box)
        self.output_text = tk.Text(
            self.root, height=15, width=70, state='normal')
        self.output_text.pack(pady=10)

        # A simple stop event
        self.stop_event = Event()

    def on_submit(self):
        """
        Called when user presses 'Send'. We gather user input and pass it
        to the CLI logic asynchronously.
        """
        user_input = self.input_box.get().strip()
        if not user_input:
            return
        # Clear the input box
        self.input_box.delete(0, tk.END)

        # We schedule the command handling inside asyncio's event loop
        asyncio.run_coroutine_threadsafe(
            self.cli_app.handle_command(user_input, speak_back=False),
            self.loop
        )

    def write_output(self, text):
        """
        Append text to the GUI's output box.
        """
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)  # auto-scroll
        self.output_text.config(state='disabled')

    def run(self):
        """
        Start the Tk main loop in a separate thread,
        while the main Python thread runs asyncio.
        """
        # In a real application, you'd properly integrate the tkinter event loop with asyncio.
        Thread(target=self._tk_thread, daemon=True).start()

    def _tk_thread(self):
        # Keep the GUI active until user closes
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        self.stop_event.set()
        self.root.quit()
