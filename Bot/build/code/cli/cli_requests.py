from Bot.build.code.tasks.coder import find_functions_without_docstrings

class CLIRequests:

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

    def list_sessions(self):
        sessions = self.session_manager.list_sessions()
        if sessions:
            print("Available session files:")
            for session in sessions:
                print(f"- {session}")
        else:
            print("No session files found.")

    async def show_chat_history(self, page: int = 1, page_size: int = 10):
        """Displays the chat history to the user with pagination."""
        if not self.messages_context:
            print("No chat history available.")
            return

        total_messages = len(self.messages_context)
        total_pages = (total_messages + page_size - 1) // page_size

        if page < 1 or page > total_pages:
            print(f"Invalid page number. Please enter a number between 1 and {
                total_pages}.")
            return

        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_messages)

        print(f"\n--- Chat History (Page {page} of {total_pages}) ---\n")
        for idx, message in enumerate(self.messages_context[start_idx:end_idx], start=start_idx + 1):
            role = message.get('role', 'Unknown').capitalize()
            content = message.get('content', '')
            print(f"{idx}. {role}: {content}\n")
        print("--- End of Chat History ---\n")

        if page < total_pages:
            proceed = input(
                "Do you want to see the next page? (y/n): ").strip().lower()
            if proceed == 'y':
                await self.show_chat_history(page=page + 1, page_size=page_size)

    def update_options(self, user_input: str):
        user_input = user_input.replace('option ', '')
        if user_input.startswith('timeout'):
            self.timeout = int(user_input.replace('timeout ', ''))
            print(f"Timeout set to {self.timeout}")
        elif user_input.startswith('default'):
            self.default_option = user_input.replace('default ', '')
            print(f"Default option set to {self.default_option}")

    def do_check_docstrings(self, arg):
        """check_docstrings <file_or_directory> - Find functions/classes without docstrings."""
        path = arg.strip() or '.'
        results = find_functions_without_docstrings(path)
        if not results:
            print("No missing docstrings found.")
        else:
            for item in results:
                print(f"Missing docstring: {item}")
