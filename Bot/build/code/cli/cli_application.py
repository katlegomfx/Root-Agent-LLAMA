import asyncio
import os
import json
import traceback

from typing import List, Dict, Any

from contextlib import suppress
from threading import Event

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout

from Bot.build.code.io_utils import write_content_to_file
import Bot.build.code.session.config
from Bot.build.code.session.constants import (
    config, ai_errors_path, error_file, gen_ai_path)
from Bot.build.code.llm.prompts import load_message_template, process_user_messages_with_model, code_corpus, add_context_to_messages, read_file_content, get_message_context_summary
from Bot.build.code.cli.cli_helpers import FilePathCompleter, CLICompleter
from Bot.build.code.session.session_management import SessionManager


class CLIApplication:
    def __init__(self):
        self.commands = ["code", "fix", "combine", "tool", "self", "save_session", "load_session",
                         "list_sessions", "option", "clear", "help", "exit"]
        self.completer = CLICompleter(self)
        self.session = PromptSession(
            history=FileHistory('readline_history.txt'),
            completer=self.completer
        )

        self.stop_event = Event()
        self.summary = ''
        self.session_manager = SessionManager('cli_session.json')

        self.config = config

        self.timeout = self.config.getint("Settings", "timeout", fallback=160)
        prompt_style_str = self.config.get(
            "Styles", "prompt_style", fallback="bold #00ff00"
        )
        self.style = Style.from_dict({"prompt": prompt_style_str})

        self.default_option = self.config.get(
            "Options", "default_option", fallback="option1"
        )

        self.background_interval = self.config.getint(
            "BackgroundTask", "interval", fallback=600
        )

        # Chat history
        self.messages_template: List[Dict[str, str]] = []
        self.messages_context: List[Dict[str, str]] = []

    async def handle_command(self, user_input: str):
        """Handle user commands."""
        try:
            if user_input.startswith("clear"):
                self.messages_context.clear()
                print("Cleared previous inputs.")

            elif user_input.startswith("code"):
                await self.process_code_request(user_input)

            elif user_input.startswith("combine"):
                await self.process_combine_request(user_input)

            elif user_input.startswith("self"):
                await self.process_self_request(user_input)

            elif user_input.startswith("tool"):
                await self.process_tool_request(user_input)

            elif user_input.startswith("fix"):
                await self.process_fix_request(user_input)

            elif user_input.startswith("save_session"):
                self.save_session()

            elif user_input.startswith("load_session"):
                self.load_session()

            elif user_input.startswith("list_sessions"):
                self.list_sessions()

            elif user_input.startswith("option"):
                self.update_options(user_input)

            elif user_input.startswith("help"):
                self.display_help()

            else:
                await self.process_generic_request(user_input)

        except Exception as e:
            self.handle_error(e, context="Command Handling")

    def save_session(self):
        """Save the current session, including chat history."""
        session_data = {
            "messages_template": self.messages_template,
            "messages_context": self.messages_context,  # Store full chat history
            "config": {
                "timeout": self.timeout,
                "default_option": self.default_option
            }
        }
        self.session_manager.save_session(session_data)


    def load_session(self):
        """Load a saved session, including chat history."""
        session_data = self.session_manager.load_session()
        if session_data:
            self.messages_template = session_data.get("messages_template", [])
            self.messages_context = session_data.get(
                "messages_context", [])  # Restore chat history
            config_data = session_data.get("config", {})
            self.timeout = config_data.get("timeout", self.timeout)
            self.default_option = config_data.get(
                "default_option", self.default_option)


    def display_help(self):
        print("""
        Welcome to CLIApplication!
        Available commands:
        - code: Process a code request.
        - fix: Suggest fixes for errors.
        - combine: Combine multiple files.
        - save_session: Save the current session.
        - load_session: Load a previous session.
        - list_sessions: List available sessions.
        - option: Update application options dynamically.
        - clear: Clear the current session context.
        - help: Display this help menu.
        - exit: Exit the application.
        """)


    async def run(self) -> None:
        while not self.stop_event.is_set():
            try:
                with patch_stdout():
                    try:
                        user_input = await self.session.prompt_async(
                            "> ",
                            completer=self.completer,
                            complete_while_typing=False,
                            style=self.style,
                        )
                    except asyncio.TimeoutError:
                        print("\nTimed out!")
                        continue

            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                self.stop_event.set()
                break

            if not user_input or user_input.startswith('exit'):
                if user_input.startswith('exit'):
                    print('Goodbye')
                break

            await self.handle_command(user_input)


    async def process_generic_request(self, user_input: str):
        """Process generic user input."""
        # Prepend session chat history to the current messages


        messages = load_message_template(
            sys_type='base', summary=self.summary) + self.messages_context
        messages.append({'role': 'user', 'content': user_input})


        # Call LLM to process the message
        response = await process_user_messages_with_model(messages)

        # Append user input and assistant response to session chat history
        self.messages_context.append({'role': 'user', 'content': user_input})
        self.messages_context.append(
            {'role': 'assistant', 'content': response})

        # print(response)
        await self.trim_context()


    async def process_code_request(self, user_input: str):
        """Process a code-related user request."""
        base_code = read_file_content('main.py')
        user_request = user_input.replace('code ', '')

        # Prepare prompt with chat history
        prompt = f"# Considering the following:\n\n{base_code}\n\n# {user_request}"
        write_content_to_file(prompt, './prompts/gen/code_prompt.md')
        messages = load_message_template(
            sys_type='python', summary=self.summary) + self.messages_context
        messages.append({'role': 'user', 'content': prompt})

        # Call LLM to process the message
        response = await process_user_messages_with_model(messages)

        # Append to chat history
        self.messages_context.append({'role': 'user', 'content': user_input})
        self.messages_context.append({'role': 'assistant', 'content': response})

        # print(response)
        await self.trim_context()

    async def process_combine_request(self, user_input: str):
        base_code = f"\n## main.py:\n{read_file_content('main.py')}\n"
        base_code += "".join(code_corpus('./Bot'))
        user_request = f'# Focus on the following:\n{user_input.replace(
            "combine ", "")}' if user_input.replace('combine ', '').strip() != '' else ''
        additional_dir = "".join(code_corpus('./idea'))
        prompt = f'# Considering the following:\n\n{
            base_code}\n\n# Incorporate the following:\n\n{additional_dir}\n\n{user_request}'
        write_content_to_file(prompt, './prompts/gen/combine_prompt.md')
        code_combine_messages = load_message_template(
            sys_type='python', summary=self.summary)
        response = await process_user_messages_with_model(code_combine_messages)

        code_combine_messages.append({'role': 'user', 'content': prompt})
        code_combine_messages.append(
            {'role': 'assistant', 'content': response})

        self.messages_context.append({'role': 'user', 'content': prompt})
        self.messages_context.append(
            {'role': 'assistant', 'content': response})
        await self.trim_context()

    async def process_self_request(self, user_input: str):
        base_code = "".join(code_corpus('./Bot'))
        user_request = user_input.replace('self ', '')
        prompt = f'# Considering the following:\n\n{
            base_code}\n\n# {user_request}'
        write_content_to_file(prompt, './prompts/gen/self_prompt.md')
        code_self_messages = load_message_template(
            sys_type='python', summary=self.summary)
        code_self_messages.append({'role': 'user', 'content': prompt})
        response = await process_user_messages_with_model(code_self_messages)
        code_self_messages.append({'role': 'assistant', 'content': response})

        self.messages_context.append({'role': 'user', 'content': prompt})
        self.messages_context.append(
            {'role': 'assistant', 'content': response})
        await self.trim_context()

    async def process_fix_request(self, user_input: str):
        """Process a fix-related user request."""
        base_code = "".join(code_corpus('./Bot'))
        error_code = read_file_content(
            os.path.join(gen_ai_path, ai_errors_path, error_file))
        user_request = user_input.replace('fix ', '')

        # Prepare prompt with chat history
        prompt = f"# Considering the following:\n\n{base_code}\n\n# What modifications need to be made in order to address the error:\n\n{error_code}"
        write_content_to_file(prompt, './prompts/gen/fix_prompt.md')
        messages = load_message_template(
            sys_type='python', summary=self.summary) + self.messages_context
        messages.append({'role': 'user', 'content': prompt})

        # Call LLM to process the message
        response = await process_user_messages_with_model(messages)

        # Append to chat history
        self.messages_context.append({'role': 'user', 'content': user_input})
        self.messages_context.append(
            {'role': 'assistant', 'content': response})

        # print(response)
        await self.trim_context()

    async def process_tool_request(self, user_input: str):
        """Process a fix-related user request."""
        
        user_request = user_input.replace('tool ', '')

        messages = load_message_template(
            sys_type='tool', summary=self.summary) + self.messages_context
        messages.append({'role': 'user', 'content': user_request})

        # Call LLM to process the message
        response = await process_user_messages_with_model(messages, tool_use=True, execute=True)

        # Append to chat history
        self.messages_context.append({'role': 'user', 'content': user_input})
        self.messages_context.append(
            {'role': 'assistant', 'content': response})

        # print(response)
        await self.trim_context()


    def set_config(self, key: str, value: str):
        """Update configuration dynamically."""
        section, option = key.split(".")
        self.config.set(section, option, value)
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)
        print(f"Configuration updated: {key} = {value}")

    async def trim_context(self, max_length: int = 28):
        """Trim the chat context to the last `max_length` interactions."""

        # Summarize if too long:
        if len(self.messages_context) > max_length:  # your threshold
            self.summary = get_message_context_summary(self.messages_context)

            # Store embeddings:
            # await store_message_in_vector_db('assistant', assistant_response)
            self.messages_context = self.messages_context[-max_length:]

    def handle_error(self, error: Exception, context: str = ""):
        """Handle errors gracefully and log debug details."""
        print(f"An error occurred: {error}")
        if self.config.getboolean("Settings", "debug", fallback=False):
            print(f"Context: {context}")
            print(f"Details: {traceback.format_exc()}")

    def list_sessions(self):
        sessions = self.session_manager.list_sessions()
        if sessions:
            print("Available session files:")
            for session in sessions:
                print(f"- {session}")
        else:
            print("No session files found.")

    def update_options(self, user_input: str):
        user_input = user_input.replace('option ', '')
        if user_input.startswith('timeout'):
            self.timeout = int(user_input.replace('timeout ', ''))
            print(f"Timeout set to {self.timeout}")
        elif user_input.startswith('default'):
            self.default_option = user_input.replace('default ', '')
            print(f"Default option set to {self.default_option}")

    def get_completer(self, document):
        word = document.get_word_before_cursor()
        if word.startswith('option'):
            return CLICompleter.option_completer
        elif word.startswith('tool'):
            return CLICompleter.tool_completer
        elif word.startswith('code'):
            return CLICompleter.code_completer
        elif word.startswith('combine'):
            return CLICompleter.combine_completer
        elif word.startswith('self'):
            return CLICompleter.self_completer
        elif word.startswith('fix'):
            return CLICompleter.fix_completer
        elif word.startswith('save_session'):
            return CLICompleter.save_session_completer
        elif word.startswith('load_session'):
            return CLICompleter.load_session_completer
        elif word.startswith('list_sessions'):
            return CLICompleter.list_sessions_completer
        elif word.startswith('exit'):
            return CLICompleter.exit_completer
        elif word.startswith('clear'):
            return CLICompleter.clear_completer
        else:
            return CLICompleter.base_completer

    async def get_self_improvement_state(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                yield data
            # Create a plan

            # Extract steps
                # Write required code

                # Save to required location

                # Do required action

                # Evalute if step complete

            # Do the next step

    async def background_task(self, interval):
        try:
            while not self.stop_event.is_set():
                await asyncio.sleep(interval)
                session_data = {
                    "messages_template": self.messages_template,
                    "messages_context": self.messages_context,
                    "config": {
                        "timeout": self.timeout,
                        "default_option": self.default_option
                    }
                }
                self.session_manager.save_session(session_data)
                print("Periodic session save completed.")
            # while not self.stop_event.is_set():
            #     await asyncio.sleep(interval)
                # try:
                #     self.get_self_improvement_state('self_improvement_state.json')
                # except Exception as e:
                #     print(f"Background task error: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Background task error: {e}")


    async def background_sender(self, input_string):
        # await asyncio.sleep(10)  # Wait 10 seconds before sending a message
        await self.handle_command(input_string)
        # Add more logic if you want to send multiple messages over time


async def main():
    cli_app = CLIApplication()

    background = asyncio.create_task(
        cli_app.background_task(cli_app.background_interval)
    )
    try:
        await cli_app.run()
    finally:
        cli_app.stop_event.set()
        background.cancel()
        with suppress(asyncio.CancelledError):
            await background


if __name__ == "__main__":
    asyncio.run(main())
