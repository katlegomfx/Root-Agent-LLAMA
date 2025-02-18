# Bot\build\code\cli\cli_application.py
import asyncio

import traceback
import speech_recognition as sr
import pyttsx3
import asyncio
import signal
import os
import json
from contextlib import suppress

from typing import List, Dict, Any

from threading import Event

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout

from Bot.build.code.gui.gui_application import GUIApplication
from Bot.build.code.cli.next.control import execute_commands
from Bot.build.code.llm.llm_client import infer
from Bot.build.code.llm.workflows import accomplished_request, decide_execution
from Bot.build.code.session.config import ensure_build_directories
from Bot.build.code.session.constants import (
    config, gen_ai_path, ai_history_path)
from Bot.build.code.llm.prompts import process_user_messages_with_model, get_message_context_summary
from Bot.build.code.cli.cli_helpers import FilePathCompleter, CLICompleter
from Bot.build.code.session.session_management import SessionManager

from Bot.build.code.cli.user_requests import UserRequests
from Bot.build.code.cli.cli_requests import CLIRequests
from Bot.build.code.cli.ai_requests import AIRequests

from Bot.build.code.utils.text_utils import strip_code_blocks

ensure_build_directories()

class CLIApplication(UserRequests, AIRequests, CLIRequests):
    def __init__(self):
        self.use_chat_history = True
        self.commands = [
            "code", "fix", "combine", "tool", "self",
            "save_session", "load_session", "list_sessions",
            "option", "clear", "help", "exit",
            "check_docstrings",
            "auto_improve", "show_history"
        ]
        self.completer = CLICompleter(self)
        self.session = PromptSession(
            history=FileHistory('readline_history.txt'),
            completer=self.completer
        )

        self.stop_event = Event()
        self.summary = ''
        self.history_file = 'history.json'
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

        self.messages_context: List[Dict[str, str]] = self.load_history()

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

    # async def speak(self, text: str):
    #     """Use TTS to speak the given text, excluding code blocks."""
    #     try:
    #         # Strip code blocks from the text
    #         clean_text = strip_code_blocks(text)
    #         if not clean_text.strip():
    #             return  # Avoid speaking if there's no meaningful text

    #         # Optionally, split text into manageable chunks to avoid overwhelming the TTS engine
    #         max_chunk_size = 500  # Adjust based on TTS capabilities
    #         chunks = [clean_text[i:i+max_chunk_size]
    #                 for i in range(0, len(clean_text), max_chunk_size)]

    #         loop = asyncio.get_event_loop()
    #         for chunk in chunks:
    #             if chunk.strip():
    #                 await loop.run_in_executor(None, self.tts_engine.say, chunk)
    #                 await loop.run_in_executor(None, self.tts_engine.runAndWait)
    #     except Exception as e:
    #         print(f"Error in TTS: {e}")

    # async def listen(self) -> str:
    #     """Listen to the microphone and return the recognized text."""
    #     with self.microphone as source:
    #         self.recognizer.adjust_for_ambient_noise(source)
    #         try:
    #             audio = await asyncio.get_event_loop().run_in_executor(None, self.recognizer.listen, source)
    #             text = self.recognizer.recognize_google(audio)
    #             return text.lower()
    #         except sr.UnknownValueError:
    #             await self.speak("Sorry, I did not understand that.")
    #             return ""
    #         except sr.RequestError:
    #             await self.speak("Sorry, I'm unable to reach the speech recognition service.")
    #             return ""

    # async def voice_command_listener(self):
    #     """Continuously listen for voice commands."""
    #     await self.speak("Voice command listener activated. Say 'hey flexi' to start.")
    #     while not self.stop_event.is_set():
    #         command = await self.listen()
    #         if "hey flexi" in command:
    #             await self.speak("Listening for your command.")
    #             user_command = await self.listen()
    #             if user_command:
    #                 if "stop" in user_command:
    #                     await self.speak("Voice command listener deactivated.")
    #                     self.stop_event.set()
    #                     break
    #                 else:
    #                     await self.handle_command(user_command)
    #     # Reset the stop_event for future use
    #     self.stop_event.clear()

    async def send_and_store_message(self, messages: List[Dict[str, str]], speak_back: bool = False, send_type='') -> str:
        """
        Sends messages to the LLM, stores the conversation in messages_context,
        and returns the assistant's response.

        Parameters:
            messages (List[Dict[str, str]]): Messages to send to the LLM.
            speak_back (bool): Whether to read the assistant's response via TTS.
        """
        try:
            if send_type == 'decide':
                response = await decide_execution(messages)
            elif send_type == 'check':
                response = await accomplished_request(messages)
            else:
                response = await process_user_messages_with_model(messages)

            # Append user message
            self.messages_context.append(messages[-1])

            # Append assistant response
            self.messages_context.append(
                {'role': 'assistant', 'content': response})

            # print(len(self.messages_context))
            # input("len(self.messages_context)")
            # Conditionally speak the assistant's response
            # if speak_back:
            #     await self.speak(response)

            await self.trim_context()
            return response
        except Exception as e:
            self.handle_error(e, context="LLM Interaction")
            return ""

    async def handle_command(self, user_input: str, speak_back: bool = True):
        """Handle user commands."""
        try:
            if user_input.startswith("clear"):
                self.messages_context.clear()
                print("Cleared previous inputs.")

            # elif user_input.startswith("start voice"):
            #     if self.voice_listener_task is None or self.voice_listener_task.done():
            #         self.voice_listener_task = asyncio.create_task(
            #             self.voice_command_listener())
            #         await self.speak("Voice command listener started.")
            #     else:
            #         await self.speak("Voice command listener is already running.")
            # elif user_input.startswith("stop voice"):
            #     if self.voice_listener_task and not self.voice_listener_task.done():
            #         self.stop_event.set()
            #         await self.voice_listener_task
            #         self.voice_listener_task = None
            #         await self.speak("Voice command listener deactivated.")
            #     else:
            #         await self.speak("Voice command listener is not running.")

            elif user_input.startswith("agent"):
                await self.process_agent_request(user_input)

            elif user_input.startswith("flex"):
                await self.process_flex_request(user_input)

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

            elif user_input.startswith("summarize"):
                await self.do_summarize(user_input)

            elif user_input.startswith("auto_improve"):
                await self.do_auto_improve(user_input.replace("auto_improve", "").strip())

            elif user_input.startswith("check_docstrings"):
                # e.g. "check_docstrings ./myfolder"
                await self.do_check_docstrings(user_input.replace("check_docstrings", "").strip())

            elif user_input.startswith("save_session"):
                self.save_session()

            elif user_input.startswith("load_session"):
                self.load_session()

            elif user_input.startswith("list_sessions"):
                self.list_sessions()

            elif user_input.startswith("option"):
                self.update_options(user_input)

            elif user_input.startswith("show_history"):
                await self.show_chat_history()

            elif user_input.startswith("help"):
                self.display_help()
            elif user_input == "build_base_nextjs":
                execute_commands()
            else:
                await self.process_generic_request(user_input)

        except Exception as e:
            self.handle_error(e, context="Command Handling")

    def set_config(self, key: str, value: str):
        """Update configuration dynamically."""
        section, option = key.split(".")
        self.config.set(section, option, value)
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)
        print(f"Configuration updated: {key} = {value}")

    def load_history(self):
        if not os.path.exists(os.path.join(gen_ai_path, ai_history_path, self.history_file)):
            return []
        with open(os.path.join(gen_ai_path, ai_history_path, self.history_file), 'r', encoding='utf-8') as file:
            return json.load(file)

    def store_history(self):
        with open(os.path.join(gen_ai_path, ai_history_path, self.history_file), 'w', encoding='utf-8') as file:
            json.dump(self.messages_context, file, indent=4, ensure_ascii=False)

    async def trim_context(self, max_length: int = 8):
        """Trim the chat context to the last `max_length` interactions."""
        # Summarize if too long:
        if len(self.messages_context) > max_length:  # your threshold
            self.summary = await get_message_context_summary(
                self.messages_context)

            # Store embeddings:
            # await store_message_in_vector_db('assistant', assistant_response)
            self.messages_context = self.messages_context[-max_length:]

        self.store_history()

    def handle_error(self, error: Exception, context: str = ""):
        """Handle errors gracefully and log debug details."""
        print(f"An error occurred: {error}")
        if self.config.getboolean("Settings", "debug", fallback=False):
            print(f"Context: {context}")
            print(f"Details: {traceback.format_exc()}")

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

            await self.handle_command(user_input, speak_back=False)

        # After exiting the loop
        # await self.speak("Application is shutting down.")

async def main():
    cli_app = CLIApplication()

    # Create the GUI object:
    gui_app = GUIApplication()

    # Start the GUI in its own thread:
    gui_app.run()

    # Create a shutdown event
    shutdown_event = asyncio.Event()

    # Define signal handler
    def handle_sigint():
        print("\nReceived exit signal. Shutting down...")
        shutdown_event.set()

    # Register signal handlers
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, handle_sigint)
    loop.add_signal_handler(signal.SIGTERM, handle_sigint)  # Optional

    # Start background tasks
    background = asyncio.create_task(
        cli_app.background_task(cli_app.background_interval)
    )

    if cli_app.voice_listener_task:
        voice_listener = asyncio.create_task(cli_app.voice_listener_task)
    else:
        voice_listener = None

    try:
        # Run the main CLI loop until shutdown_event is set
        await asyncio.wait(
            [cli_app.run(), shutdown_event.wait()],
            return_when=asyncio.FIRST_COMPLETED
        )
    finally:
        # Initiate shutdown
        cli_app.stop_event.set()

        # Cancel background tasks
        tasks_to_cancel = [background]
        if voice_listener:
            tasks_to_cancel.append(voice_listener)

        for task in tasks_to_cancel:
            task.cancel()

        # Wait for tasks to cancel gracefully
        with suppress(asyncio.CancelledError):
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

        # Save the session if needed
        cli_app.save_session()

        # Speak shutdown message
        # await cli_app.speak("Application is shutting down.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
