import os
import json
class SessionManager:
    def __init__(self, session_file: str = 'session.json'):
        self.session_file = session_file
        if os.path.exists(self.session_file):
            restore = input("Restore the last session? (y/n): ").strip().lower()
            if restore == 'y':
                self.load_session()

    def autosave_session(self):
        """Automatically save the session after every command if enabled."""
        if self.config.getboolean("Settings", "autosave", fallback=True):
            self.save_session()



    def save_session(self, session_data: dict) -> None:
        """Save session data to a JSON file."""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=4)
            print(f"Session successfully saved to {self.session_file}.")
        except Exception as e:
            print(f"Error saving session: {e}")

    def load_session(self) -> dict:
        """Load session data from a JSON file."""
        if not os.path.exists(self.session_file):
            print(f"Session file {self.session_file} does not exist.")
            return {}

        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            print(f"Session successfully loaded from {self.session_file}.")
            return session_data
        except Exception as e:
            print(f"Error loading session: {e}")
            return {}

    def list_sessions(self, directory: str = '.') -> list:
        """List all available session files in a directory."""
        return [f for f in os.listdir(directory) if f.endswith('.json')]
