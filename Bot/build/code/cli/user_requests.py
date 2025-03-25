# Bot\build\code\cli\user_requests.py
import os
import sys
import traceback

from colorama import Fore

from Bot.build.code.cli.cli_helpers import colored_print
from Bot.build.code.cli.next.info.add_path import prepend_file_location_check
from Bot.build.code.cli.next.info.dry_check import find_similar_code_in_directory
from Bot.build.code.cli.next.info.line_cleaner import process_directory
from Bot.build.code.llm.workflows import code_use, tool_use
from Bot.build.code.session.constants import (
    ai_errors_path, error_file, gen_ai_path, tips)
from Bot.build.code.llm.prompts import convert_to_md, get_ts_files_content, load_message_template, code_corpus, read_file_content
from Bot.build.code.io_utils import write_content_to_file

class UserRequests:

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
        - show_history: Display the chat history.
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

    async def process_generic_request(self, user_input: str):
        """Process generic user input."""
        # Prepend session chat history to the current messages

        messages = self.messages_context + load_message_template(
            sys_type='general', summary=self.summary)
        messages.append({'role': 'user', 'content': user_input})

        response = await self.send_and_store_message(messages)

    async def process_code_request(self, user_input: str):
        """Process a code-related user request."""
        base_code = read_file_content('main.py')
        user_request = user_input.replace('code ', '')

        # Prepare prompt with chat history
        prompt = f"# Considering the following:\n\n{
            base_code}\n\n# {user_request}\n\n{tips}"
        write_content_to_file(prompt, './prompts/gen/code_prompt.md')
        code_messages = self.messages_context + load_message_template(
            sys_type='python', summary=self.summary)
        code_messages.append({'role': 'user', 'content': prompt})

        response = await self.send_and_store_message(code_messages)

    async def process_combine_request(self, user_input: str):
        base_code = "".join(code_corpus('./Bot'))
        user_request = f'\n\n# Focus on the following:\n{user_input.replace(
            "combine ", "")}' if user_input.replace('combine ', '').strip() != '' else ''
        additional_dir = "".join(code_corpus('./idea'))
        # additional_dir = "".join(code_corpus('./idea'))
        prompt = f'# Considering the following:\n\n{
            base_code}\n\n# Incorporate the following:\n\n{additional_dir}{user_request}'

        write_content_to_file(prompt, './prompts/gen/combine_prompt.md')

        code_combine_messages = self.messages_context + load_message_template(
            sys_type='python', summary=self.summary)
        # Ensure prompt is appended
        code_combine_messages.append({'role': 'user', 'content': prompt})

        response = await self.send_and_store_message(code_combine_messages)

    async def process_flex_request(self, user_input: str):
        base_code = "".join(code_corpus('./Bot'))

        goal = f"Incorporate the following:\n\n## main.py:\n{
            read_file_content('main.py')}\n"
        user_request = user_input.replace('flex ', '')

        if len(user_request) >= 3:
            final_request = f"\n\n# {user_request}"
            prompt = f'# Considering the following:\n\n{
                base_code}\n\n# {goal}{final_request}\n\n{tips}'
        else:
            prompt = f'# Considering the following:\n\n{
                base_code}\n\n# {goal}\n\n{tips}'

        write_content_to_file(prompt, './prompts/gen/flex_prompt.md')

        code_flex_messages = self.messages_context + \
            load_message_template(sys_type='python', summary=self.summary)
        code_flex_messages.append({'role': 'user', 'content': prompt})
        response = await self.send_and_store_message(code_flex_messages)

    async def process_self_request(self, user_input: str):
        directory_to_process = "."
        extensions_to_process = ('.py')
        files_to_keep = [
            "next-env.d.js",
            "next.config.js",
            "package.json",
            "postcss.config.js",
            "tailwind.config.js",
            "jsconfig.json"
        ]
        ignored_directories = ["node_modules",
                               ".next", "jsBuild", "jsBuilds", "pyllms", "pyds", "results"]

        prepend_file_location_check(
            directory_to_process, extensions_to_process, files_to_keep, ignored_directories)

        directory_to_process = "."
        extensions_to_process = ('.py',)
        ignored_directories = ["node_modules",
                               ".next", "jsBuild", "jsBuilds", "results", "pyds"]

        # Get the list of matching files
        # files_with_headers = list_files_with_comment_header(
        #     directory_to_process, extensions_to_process, ignored_directories)

        similar_code_pieces = find_similar_code_in_directory(
            './Bot', min_match_lines=4)

        output_filepath = "prompts/report_similar_code.md"
        write_content_to_file(similar_code_pieces, output_filepath)

        process_directory('./Bot')

        base_code = "".join(code_corpus('./Bot'))
        user_request = user_input.replace('self ', '')
        prompt = f'# Codebase:\n\n{
            base_code}\n\n# {user_request}\n\n{tips}'
        write_content_to_file(prompt, './prompts/gen/self_prompt.md')
        code_self_messages = self.messages_context + load_message_template(
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
        prompt = f"# Considering the following:\n\n{
            base_code}\n\n# What modifications need to be made in order to address the error:\n\n{error_code}\n\n{tips}"
        write_content_to_file(prompt, './prompts/gen/fix_prompt.md')
        fix_messages = self.messages_context + load_message_template(
            sys_type='python', summary=self.summary)
        fix_messages.append({'role': 'user', 'content': prompt})

        response = await self.send_and_store_message(fix_messages)

    async def process_tool_request(self, user_input: str):
        """Process a fix-related user request."""

        user_request = user_input.replace('tool ', '')

        messages = self.messages_context + load_message_template(
            sys_type='tool', summary=self.summary)
        messages.append({'role': 'user', 'content': user_request})

        # Call LLM to process the message
        response = await tool_use(messages)

        # Append to chat history
        self.messages_context.append({'role': 'user', 'content': user_input})
        self.messages_context.append(
            {'role': 'assistant', 'content': response})

        # print(response)
        await self.trim_context()

    async def process_agent_request(self, user_input: str, tries=0):
        base_code = "".join(code_corpus('./Bot'))
        user_request = user_input.replace('agent ', '')
        if len(user_request) >= 3:
            final_request = f"\n\n# {user_request}"
            prompt = f'# Considering the following:\n\n{
                base_code}{final_request}'
        else:
            prompt = f'# Considering the following:\n\n{
                base_code}'

        write_content_to_file(prompt, './prompts/gen/agent_prompt.md')

        responses = []

        state = False
        while not state or tries < 5:
            try:
                colored_print("Deciding using AI", Fore.GREEN)
                base_prompt = self.messages_context + \
                    load_message_template('base', self.summary)
                base_prompt.append({"role": "user", "content": prompt})

                # print(prompt)
                # print(len(base_prompt))
                # print(len([message["content"]
                #       for message in base_prompt if message["role"] == 'user'][0]))
                # input("base_prompt")

                ai_choice = await self.send_and_store_message(base_prompt, send_type='decide')

                if ai_choice == "python":
                    colored_print("Starting Python Code Use", Fore.GREEN)
                    base_prompt = self.messages_context + \
                        load_message_template('python')
                    base_prompt.append(prompt)
                    final_response, code_script, status_message, base_prompt = await code_use(base_prompt)
                    responses.append(
                        {
                            'response': final_response,
                            'code': code_script,
                            'status': status_message,
                            'request': base_prompt
                        }
                    )

                elif ai_choice == "tool":
                    colored_print("Starting Tool Use", Fore.GREEN)
                    base_prompt = self.messages_context + \
                        load_message_template('tool')
                    base_prompt.append(prompt)
                    base_response, code_script, status_message, base_prompt = await tool_use(base_prompt)
                    responses.append(
                        {
                            'response': base_response,
                            'instruction': code_script,
                            'status': status_message,
                            'request': base_prompt
                        }
                    )
                else:
                    colored_print("No valid option provided", Fore.CYAN)

            except Exception as e:
                with open("error.log", "w", encoding="utf-8") as err_file:
                    err_file.write("An unhandled error occurred:")
                    traceback.print_exc(file=err_file)
                error_text = open("error.log", "r", encoding="utf-8").read()
                base_prompt = self.messages_context + \
                    load_message_template('python')
                base_prompt.append({
                    'role': 'user',
                    'content': f"Look at the following error:\n{error_text}\nIn the code:\n{base_code}\nHow can we fix this error"
                })
                fix_res = await self.send_and_store_message(base_prompt)
                open("error_fix.md", "w", encoding="utf-8").write(fix_res)
                sys.exit(1)

            finally:
                colored_print("Checking task was completed", Fore.GREEN)
                tries += 1
                check_prompt = self.messages_context + \
                    load_message_template('check', self.summary)
                check_prompt.append(
                    {
                        'role': 'user',
                        'content': responses
                    }
                )

                print(check_prompt)
                input("check_prompt")

                ai_choice = await self.send_and_store_message(base_prompt, send_type='check')
                if 'no' not in ai_choice:
                    state = True

    async def process_video_request(self, user_input: str, tries=0):
        base_code = "".join(code_corpus('./video'))
        user_request = user_input.replace('video ', '')
        if len(user_request) >= 3:
            final_request = f"\n\n# {user_request}"
            prompt = f'# Considering the following:\n\n{
                base_code}{final_request}\n\n{tips}'
        else:
            prompt = f'# Considering the following:\n\n{
                base_code}'

        write_content_to_file(prompt, './prompts/gen/video_prompt.md')

    async def process_simple_request(self, user_input: str, tries=0):


        directory1 = "./app/base"
        ts_files_1 = convert_to_md(get_ts_files_content(directory1))

        directory2 = "./app/appgen"
        ts_files_2 = convert_to_md(get_ts_files_content(directory2))




        base_code = "".join(code_corpus('./simple'))
        user_request = user_input.replace('simple ', '')
        if len(user_request) >= 3:
            final_request = f"\n\n# {user_request}"
            prompt = f'''# Considering the following:\n\n{
                base_code}{final_request}\n\n{tips}'''
        else:
            prompt = f'# Considering the following:\n\n{
                base_code}'

        write_content_to_file(prompt, './prompts/gen/simple_prompt.md')

        # code_messages = self.messages_context + load_message_template(
        #     sys_type='python', summary=self.summary)
        # code_messages.append({'role': 'user', 'content': prompt})

        # response = await self.send_and_store_message(code_messages)
