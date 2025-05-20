# long_term_memory.py
import json
import uuid
import os
from datetime import datetime

LTM_PATH = "memory/long_term_memory.json"

class LongTermMemory:
    def __init__(self, path=LTM_PATH):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.isfile(path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def save(self, speaker, message, tags=None, metadata=None):
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "speaker": speaker,
            "message": message,
            "tags": tags or [],
            "metadata": metadata or {}
        }
        entries = self.load_all()
        entries.append(entry)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)

    def load_all(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def summarize(self, max_items=10):
        return [
            f"{e['timestamp'][:19]} | {e['speaker']}: {e['message']}"
            for e in self.load_all()[-max_items:]
        ]

    def search(self, keyword):
        return [e for e in self.load_all() if keyword.lower() in e["message"].lower()]

    def find_by_tag(self, tag):
        return [e for e in self.load_all() if tag in e.get("tags", [])]
