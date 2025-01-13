import os

from Bot.build.code.cli.next.info.add_path import prepend_file_location_check
from Bot.build.code.cli.next.info.code_cleaner import list_files_with_comment_header
from Bot.build.code.cli.next.info.line_cleaner import process_directory
from Bot.build.code.session.constants import (
    config, ai_errors_path, error_file, gen_ai_path)
from Bot.build.code.llm.prompts import load_message_template, process_user_messages_with_model, code_corpus, read_file_content
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

        messages = load_message_template(
            sys_type='base', summary=self.summary) + self.messages_context
        messages.append({'role': 'user', 'content': user_input})

        response = await self.send_and_store_message(messages)

    async def process_code_request(self, user_input: str):
        """Process a code-related user request."""
        base_code = read_file_content('main.py')
        user_request = user_input.replace('code ', '')

        # Prepare prompt with chat history
        prompt = f"# Considering the following:\n\n{
            base_code}\n\n# {user_request}"
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
        # additional_dir = "".join(code_corpus('./idea'))
        prompt = f'# Considering the following:\n\n{
            base_code}\n\n# Incorporate the following:\n\n{additional_dir}{user_request}'

        write_content_to_file(prompt, './prompts/gen/combine_prompt.md')

        code_combine_messages = load_message_template(
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
                base_code}\n\n# {goal}{final_request}'
        else:
            prompt = f'# Considering the following:\n\n{
                base_code}\n\n# {goal}'

        write_content_to_file(prompt, './prompts/gen/flex_prompt.md')

        code_flex_messages = load_message_template(
            sys_type='python', summary=self.summary)
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
                            ".next", "jsBuild", "jsBuilds", "pyllms", "results"]

        prepend_file_location_check(
            directory_to_process, extensions_to_process, files_to_keep, ignored_directories)
        
        directory_to_process = "."
        extensions_to_process = ('.py',)
        ignored_directories = ["node_modules",
                            ".next", "jsBuild", "jsBuilds", "results"]

        # Get the list of matching files
        files_with_headers = list_files_with_comment_header(
            directory_to_process, extensions_to_process, ignored_directories)
        
        process_directory('./Bot')
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
        prompt = f"# Considering the following:\n\n{
            base_code}\n\n# What modifications need to be made in order to address the error:\n\n{error_code}"
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
