import json
import uuid
import os
import atexit
from datetime import datetime

LTM_PATH = "memory/long_term_memory.json"

class LongTermMemory:
    def __init__(self, path=LTM_PATH):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.isfile(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f)
        self.memory = self._load_all()
        atexit.register(self._write_all)  # Auto-save on exit

    def _load_all(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_all(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2)

    def save(self, speaker, message, tags=None, metadata=None):
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "speaker": speaker,
            "message": message,
            "tags": tags or [],
            "metadata": metadata or {}
        }
        self.memory.append(entry)
        self._write_all()

    def summarize(self, max_items=10):
        return [
            f"{e['timestamp'][:19]} | {e['speaker']}: {e['message']}"
            for e in self.memory[-max_items:]
        ]

    def search(self, keyword):
        return [e for e in self.memory if keyword.lower() in e["message"].lower()]

    def find_by_tag(self, tag):
        return [e for e in self.memory if tag in e.get("tags", [])]

    def ingest_book(self, file_path, chunk_size=500):
        """
        Reads a book from a .txt file and stores it in LTM as 'book_chunk' entries.
        """
        if not os.path.isfile(file_path):
            return f"Book file not found: {file_path}"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

            for i, chunk in enumerate(chunks):
                self.save(
                    speaker="Book",
                    message=chunk.strip(),
                    tags=["book", "ingested"],
                    metadata={"chunk_index": i, "source_file": os.path.basename(file_path)}
                )

            return f"Ingested {len(chunks)} chunks from {os.path.basename(file_path)}."

        except Exception as e:
            return f"Error during book ingestion: {e}"
