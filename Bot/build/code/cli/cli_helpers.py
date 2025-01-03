import os
import glob
import shlex

from prompt_toolkit.completion import Completer, Completion

class FilePathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        dirname, partial_filename = os.path.split(text)
        if not dirname:
            dirname = "."
        pattern = os.path.join(dirname, partial_filename + "*")
        for path in glob.glob(pattern):
            if os.path.isdir(path):
                display = path + os.sep
            else:
                display = path
            yield Completion(display, start_position=-len(partial_filename))


class CLICompleter(Completer):
    def __init__(self, cli_app):
        self.cli_app = cli_app

    def get_completions(self, document, complete_event):
        try:
            text = document.text_before_cursor
            words = shlex.split(text)
            if not words:
                return

            if document.cursor_position != len(text):
                return

            command = words[0]
            args = words[1:]

            if len(words) == 1:
                matches = [
                    cmd for cmd in self.cli_app.commands if cmd.startswith(command)
                ]
                for match in matches:
                    yield Completion(match, start_position=-len(command))
            else:
                completer_method = getattr(
                    self.cli_app, f"complete_{command}", None)
                if completer_method:
                    completions = completer_method(text, args)
                    last_arg = args[-1] if args else ""
                    for completion in completions:
                        if completion.startswith(last_arg):
                            yield Completion(completion, start_position=-len(last_arg))
        except Exception as e:
            print(f"Completer error: {e}")

            # logging.error(f"Completer error: {e}", exc_info=True)
