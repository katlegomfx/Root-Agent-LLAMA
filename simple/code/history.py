import os
import json
from datetime import datetime
from typing import Any, List, Optional
import logging
from simple.code.logging_config import setup_logging

# Centralized logging setup
setup_logging()


class HistoryManager:
    def __init__(self, history_dir: str = "simple/gag/history") -> None:
        self.history_dir = history_dir
        os.makedirs(self.history_dir, exist_ok=True)
        self.current_file: Optional[str] = None

    def get_history_files(self) -> List[str]:
        return [f for f in os.listdir(self.history_dir) if f.endswith(".json")]

    def save_history(self, history_data: Any, filename: str = "") -> Optional[str]:
        if not filename:
            if not self.current_file:
                filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                filename = self.current_file
        elif not filename.endswith(".json"):
            filename += ".json"
        self.current_file = filename
        path = os.path.join(self.history_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=4)
            logging.info(f"History saved to {path}")
            return path
        except Exception as e:
            logging.error(f"Error saving history: {e}")
            return None

    def load_history(self, filename: str) -> Optional[Any]:
        path = os.path.join(self.history_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                history = json.load(f)
            self.current_file = filename
            logging.info(f"History loaded from {path}")
            return history
        except Exception as e:
            logging.error(f"Error loading history from {path}: {e}")
            return None

    def delete_history(self, filename: str) -> None:
        path = os.path.join(self.history_dir, filename)
        try:
            if os.path.exists(path):
                os.remove(path)
                logging.info(f"Deleted history file: {path}")
            else:
                logging.warning(f"History file {path} does not exist.")
        except Exception as e:
            logging.error(f"Error deleting history file {path}: {e}")
