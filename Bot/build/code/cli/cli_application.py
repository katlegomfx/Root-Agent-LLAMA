import asyncio
import os
import json
import traceback
import speech_recognition as sr
import pyttsx3
import asyncio


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
from Bot.build.code.tasks.coder import find_functions_without_docstrings
from Bot.build.code.tasks.improver import analyze, improve, refine


from Bot.build.code.utils.text_utils import strip_code_blocks


class CLIApplication:
    def __init__(self):
        self.use_chat_history = True
        self.commands = [
            "code", "fix", "combine", "tool", "self",
            "save_session", "load_session", "list_sessions",
            "option", "clear", "help", "exit",
            "check_docstrings",
            "auto_improve"
        ]
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

        self.initial_state = {"auto_improve": "Not Started"}

        self.agent_facts = {
            "last_tool_result": None,
            "last_tool_name": None,
        }

            # Initialize Speech Recognition and TTS
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)

        self.voice_listener_task = None

    async def speak(self, text: str):
        """Use TTS to speak the given text, excluding code blocks."""
        try:
            # Strip code blocks from the text
            clean_text = strip_code_blocks(text)
            if not clean_text.strip():
                return  # Avoid speaking if there's no meaningful text

            # Optionally, split text into manageable chunks to avoid overwhelming the TTS engine
            max_chunk_size = 500  # Adjust based on TTS capabilities
            chunks = [clean_text[i:i+max_chunk_size]
                    for i in range(0, len(clean_text), max_chunk_size)]

            loop = asyncio.get_event_loop()
            for chunk in chunks:
                if chunk.strip():
                    await loop.run_in_executor(None, self.tts_engine.say, chunk)
                    await loop.run_in_executor(None, self.tts_engine.runAndWait)
        except Exception as e:
            print(f"Error in TTS: {e}")



    async def listen(self) -> str:
        """Listen to the microphone and return the recognized text."""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = await asyncio.get_event_loop().run_in_executor(None, self.recognizer.listen, source)
                text = self.recognizer.recognize_google(audio)
                return text.lower()
            except sr.UnknownValueError:
                await self.speak("Sorry, I did not understand that.")
                return ""
            except sr.RequestError:
                await self.speak("Sorry, I'm unable to reach the speech recognition service.")
                return ""
            
    # Inside the CLIApplication class

    async def voice_command_listener(self):
        """Continuously listen for voice commands."""
        await self.speak("Voice command listener activated. Say 'hey flexi' to start.")
        while not self.stop_event.is_set():
            command = await self.listen()
            if "hey flexi" in command:
                await self.speak("Listening for your command.")
                user_command = await self.listen()
                if user_command:
                    if "stop" in user_command:
                        await self.speak("Voice command listener deactivated.")
                        self.stop_event.set()
                        break
                    else:
                        await self.handle_command(user_command)
        # Reset the stop_event for future use
        self.stop_event.clear()

    async def send_and_store_message(self, messages: List[Dict[str, str]], speak_back: bool = True) -> str:
        """
        Sends messages to the LLM, stores the conversation in messages_context,
        and returns the assistant's response.

        Parameters:
            messages (List[Dict[str, str]]): Messages to send to the LLM.
            speak_back (bool): Whether to read the assistant's response via TTS.
        """
        try:
            response = await process_user_messages_with_model(messages)
            # Append user messages
            for message in messages:
                self.messages_context.append(message)
            # Append assistant response
            self.messages_context.append(
                {'role': 'assistant', 'content': response})
            # Conditionally speak the assistant's response
            if speak_back:
                await self.speak(response)
            await self.trim_context()
            return response
        except Exception as e:
            self.handle_error(e, context="LLM Interaction")
            return ""

    async def handle_command(self, user_input: str):
        """Handle user commands."""
        try:
            if user_input.startswith("clear"):
                self.messages_context.clear()
                print("Cleared previous inputs.")

            elif user_input.startswith("flexFile"):
                await self.process_flex_request(user_input)

            elif user_input.startswith("auto_improve"):
                await self.do_auto_improve(user_input.replace("auto_improve", "").strip())

            elif user_input.startswith("start voice"):
                asyncio.create_task(self.voice_command_listener())

            elif user_input.startswith("stop voice"):
                await self.speak("Voice command listener is stopping.")
                self.stop_event.set()

            elif user_input.startswith("summarize"):
                self.do_summarize(user_input)

            elif user_input.startswith("check_docstrings"):
                # e.g. "check_docstrings ./myfolder"
                await self.do_check_docstrings(user_input.replace("check_docstrings", "").strip())

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
        - self: self multiple files.
        - check_docstrings: check_docstrings multiple files.
        - auto_improve: auto_improve multiple files.
        - summarize: summarize multiple files.
        - start voice: Activate voice command listener.
        - stop voice: Deactivate voice command listener.
            
        - save_session: Save the current session.
        - load_session: Load a previous session.
        - list_sessions: List available sessions.
            
        - option: Update application options dynamically.
            
        - clear: Clear the current session context.
        - help: Display this help menu.
        - exit: Exit the application.
        """)


    # Inside the CLIApplication class

    async def run(self) -> None:
        # Start the voice command listener if needed
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
                self.stop_event.set()
                break

            await self.handle_command(user_input)

        # After exiting the loop
        await self.speak("Application is shutting down.")


    async def process_generic_request(self, user_input: str):
        """Process generic user input."""
        # Prepend session chat history to the current messages


        messages = load_message_template(
            sys_type='base', summary=self.summary) + self.messages_context
        messages.append({'role': 'user', 'content': user_input})

        response = await self.send_and_store_message(messages)


    async def process_code_request(self, user_input: str):
        """Process a code-related user request."""
        base_code = read_file_content('main.py')
        user_request = user_input.replace('code ', '')

        # Prepare prompt with chat history
        prompt = f"# Considering the following:\n\n{base_code}\n\n# {user_request}"
        write_content_to_file(prompt, './prompts/gen/code_prompt.md')
        code_messages = load_message_template(
            sys_type='python', summary=self.summary) + self.messages_context
        code_messages.append({'role': 'user', 'content': prompt})

        response = await self.send_and_store_message(code_messages)

    async def process_combine_request(self, user_input: str):
        base_code = "".join(code_corpus('./Bot'))
        user_request = f'\n\n# Focus on the following:\n{user_input.replace(
            "combine ", "")}' if user_input.replace('combine ', '').strip() != '' else ''
        additional_dir = "".join(code_corpus('./idea'))
        prompt = f'# Considering the following:\n\n{
            base_code}\n\n# Incorporate the following:\n\n{additional_dir}{user_request}'

        write_content_to_file(prompt, './prompts/gen/combine_prompt.md')

        code_combine_messages = load_message_template(
            sys_type='python', summary=self.summary)
        
        response = await self.send_and_store_message(code_combine_messages)


    async def do_auto_improve(self, arg):
        """
        Automatically improves the initial state by creating a plan, executing steps,        
        and checking for completion.

        Args:
            initial_state (dict): The initial state to be improved.

        Returns:
            dict: The final improved state.
        """
        # Load self_improvement_state.json if it exists
        path = 'self_improvement_state.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
            # Possibly feed that into a prompt
            prompt = f"Given the self-improvement plan: {data}..."
            # Initialize an empty dictionary to store improvements
            improvements = data
        else:
            prompt = "No existing plan. Start from scratch..."
            improvements = {}

        # Define the possible steps to be taken in each iteration
        steps = [
            {
                "step": "Analyze",
                "action": analyze,
                "params": {"state": self.initial_state}
            },
            {
                "step": "Improve",
                "action": improve,
                "params": {"state": self.initial_state}
            },
            {
                "step": "Refine",
                "action": refine,
                "params": {"state": self.initial_state}
            }
        ]

        # Initialize the current state
        current_state = self.initial_state

        # Loop until all steps are completed
        while len(steps) > 0:
            # Select the next step to be executed
            next_step = steps.pop(0)

            # Check if the step is already in progress
            if "in_progress" in current_state and current_state["in_progress"] == next_step["step"]:
                print(f"Skipping {next_step['step']}, it's already in progress.")
                continue

            messages = load_message_template(sys_type='base')
            messages.append({'role': 'user', 'content': prompt})
            # Execute the selected step
            result = await process_user_messages_with_model(messages, tool_use=True, execute=True)

            # Check for completion
            if "completed" in current_state:
                if not current_state["completed"] and next_step["action"] == refine:
                    print(
                        f"{next_step['step']} was not completed, skipping to the next iteration.")
                    continue

            # Update the current state with the result of the step execution
            improvements[next_step["step"]] = {"result": result}

            # Update the in_progress flag if the step is completed
            if "completed" not in current_state and result:
                current_state["in_progress"] = next_step["step"]
                print(f"{next_step['step']} was completed.")

        return improvements


    async def do_summarize(self, arg):
        """Summarize the chat or code context."""
        if not self.messages_context:
            print("No context to summarize.")
            return
        summary_result = await get_message_context_summary(self.messages_context)
        print("Summary:", summary_result)

    def do_check_docstrings(self, arg):
        """check_docstrings <file_or_directory> - Find functions/classes without docstrings."""
        path = arg.strip() or '.'
        results = find_functions_without_docstrings(path)
        if not results:
            print("No missing docstrings found.")
        else:
            for item in results:
                print(f"Missing docstring: {item}")

    async def process_flex_request(self, user_input: str):
        base_code = "".join(code_corpus('./Bot'))

        goal = f"Incorporate the following:\n\n## main.py:\n{
            read_file_content('main.py')}\n"
        user_request = user_input.replace('flex ', '')

        if len(user_request) >= 3:
            final_request = f"\n\n# {user_request}"
            prompt = f'# Considering the following:\n\n{
                base_code}\n\n# {goal}{final_request}'
        else:
            prompt = f'# Considering the following:\n\n{
                base_code}\n\n# {goal}'

        write_content_to_file(prompt, './prompts/gen/self_prompt.md')

        code_flex_messages = load_message_template(
            sys_type='python', summary=self.summary)
        code_flex_messages.append({'role': 'user', 'content': prompt})
        response = await self.send_and_store_message(code_flex_messages)

    async def process_self_request(self, user_input: str):
        base_code = "".join(code_corpus('./Bot'))
        user_request = user_input.replace('self ', '')
        prompt = f'# Considering the following:\n\n{
            base_code}\n\n# {user_request}'
        write_content_to_file(prompt, './prompts/gen/self_prompt.md')
        code_self_messages = load_message_template(
            sys_type='python', summary=self.summary)
        code_self_messages.append({'role': 'user', 'content': prompt})
        response = await self.send_and_store_message(code_self_messages)

    async def process_fix_request(self, user_input: str):
        """Process a fix-related user request."""
        base_code = "".join(code_corpus('./Bot'))
        error_code = read_file_content(
            os.path.join(gen_ai_path, ai_errors_path, error_file))
        user_request = user_input.replace('fix ', '')

        # Prepare prompt with chat history
        prompt = f"# Considering the following:\n\n{base_code}\n\n# What modifications need to be made in order to address the error:\n\n{error_code}"
        write_content_to_file(prompt, './prompts/gen/fix_prompt.md')
        fix_messages = load_message_template(
            sys_type='python', summary=self.summary) + self.messages_context
        fix_messages.append({'role': 'user', 'content': prompt})

        response = await self.send_and_store_message(fix_messages)

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

    async def background_task(self, interval):
        try:
            while not self.stop_event.is_set():
                await asyncio.sleep(interval)
                await self.do_self_improve('')
                session_data = {
                    "messages_template": self.messages_template,
                    "messages_context": self.messages_context,
                    "config": {
                        "timeout": self.timeout,
                        "default_option": self.default_option
                    }
                }
                self.session_manager.save_session(session_data)
                print("Periodic session improvement completed.")
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
