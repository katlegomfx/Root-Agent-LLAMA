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
        # A dictionary of command → possible subcommands or arguments
        self.subcommands = {
            'tool': ['bash_command', 'fetch_url_content', 'http_post_data'],
            'code': ['--execute', '--dry-run'],
            'option': ['timeout', 'default'],
            # ...
        }

    def get_completions(self, document, complete_event):
        try:
            text = document.text_before_cursor
            words = shlex.split(text)
            if not words:
                return

            if document.cursor_position != len(text):
                # If cursor is not at the end, we might skip advanced logic
                return

            command = words[0]
            args = words[1:]

            # 1) If there's only one word typed, we match top-level commands:
            if len(words) == 1:
                # Return all matching commands
                matches = [
                    cmd for cmd in self.cli_app.commands if cmd.startswith(command)
                ]
                for match in matches:
                    yield Completion(match, start_position=-len(command))

            # 2) If the command has been fully typed, look for subcommands/args
            else:
                # If we have recognized subcommands for this command:
                if command in self.subcommands:
                    last_arg = args[-1] if args else ""
                    possible_subcommands = self.subcommands[command]
                    for sc in possible_subcommands:
                        if sc.startswith(last_arg):
                            yield Completion(sc, start_position=-len(last_arg))

                # 3) Otherwise, fall back to existing logic:
                completer_method = getattr(
                    self.cli_app, f"complete_{command}", None
                )
                if completer_method:
                    completions = completer_method(text, args)
                    last_arg = args[-1] if args else ""
                    for completion in completions:
                        if completion.startswith(last_arg):
                            yield Completion(completion, start_position=-len(last_arg))

        except Exception as e:
            print(f"Completer error: {e}")
