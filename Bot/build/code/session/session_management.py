# Bot\build\code\session\session_management.py
import os
import json
from typing import Optional

from Bot.build.code.tasks.improver import analyze, improve, refine
from .state import SelfImprovementState, Step

class SessionManager:
    def __init__(self, session_file: str = 'session.json'):
        self.session_file = session_file
        self.state: Optional[SelfImprovementState] = None
        if os.path.exists(self.session_file):
            restore = input(
                "Restore the last session? (y/n): ").strip().lower()
            if restore == 'y':
                self.load_session()

    def save_session(self):
        """Save session data to a JSON file."""
        try:
            if self.state:
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(self.state.__dict__, f, indent=4)
                print(f"Session successfully saved to {self.session_file}.")
            else:
                print("No session state to save.")
        except Exception as e:
            print(f"Error saving session: {e}")

    def load_session(self):
        """Load session data from a JSON file."""
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            ### Reconstruct SelfImprovementState            steps = [Step(**step) for step in data.get('steps', [])]
            self.state = SelfImprovementState(
                steps=steps,
                improvements=data.get('improvements', {}),
                current_step_index=data.get('current_step_index', 0),
                completed=data.get('completed', False)
            )
            print(f"Session successfully loaded from {self.session_file}.")
        except Exception as e:
            print(f"Error loading session: {e}")
            self.state = None

    def initialize_new_session(self):
        """Initialize a new self-improvement session."""
        self.state = SelfImprovementState(
            steps=[
                Step(name="Analyze", action=analyze, params={"state": {}}),
                Step(name="Improve", action=improve, params={"state": {}}),
                Step(name="Refine", action=refine, params={"state": {}})
            ]
        )
        self.save_session()

    def list_sessions(self, directory: str = '.') -> list:
        """List all available session files in a directory."""
        return [f for f in os.listdir(directory) if f.endswith('.json')]
