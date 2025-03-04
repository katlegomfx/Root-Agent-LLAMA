import os
import json
from datetime import datetime


class HistoryManager:
    def __init__(self, history_dir="history"):
        self.history_dir = history_dir
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
        self.current_file = None

    def get_history_files(self):
        return [f for f in os.listdir(self.history_dir) if f.endswith(".json")]

    def save_history(self, history_data, filename=""):
        if not filename:
            if not self.current_file:
                filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                filename = self.current_file
        elif not filename.endswith(".json"):
            filename += ".json"
        self.current_file = filename
        path = os.path.join(self.history_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=4)
        return path

    def load_history(self, filename):
        path = os.path.join(self.history_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
        self.current_file = filename
        return history

    def delete_history(self, filename):
        path = os.path.join(self.history_dir, filename)
        os.remove(path)
