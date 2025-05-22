import os
import datetime

class EbookMemory:
    def __init__(self, storage_path="logs/ebooks"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    def store_book(self, title, content):
        safe_title = title.replace(" ", "_").replace("/", "_")
        filename = os.path.join(self.storage_path, f"{safe_title}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    def get_recent_books(self, n=3):
        files = sorted(
            [os.path.join(self.storage_path, f) for f in os.listdir(self.storage_path)],
            key=os.path.getmtime,
            reverse=True
        )
        return files[:n]

    def sample_passage_for_dream(self):
        import random
        books = self.get_recent_books(n=5)
        if not books:
            return None

        chosen = random.choice(books)
        with open(chosen, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return None
            excerpt = " ".join(random.sample(lines, min(5, len(lines))))
            return f"Excerpt from '{os.path.basename(chosen)}':\n{excerpt}"

    def list_titles(self):
        return [os.path.splitext(f)[0] for f in os.listdir(self.storage_path)]

    def reflect_on_books(self, trait_engine, goal_tracker):
        books = self.get_recent_books(n=2)
        if not books:
            return "I haven't read anything recently."

        reflections = []
        for path in books:
            title = os.path.splitext(os.path.basename(path))[0]
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if not lines:
                    continue
                sample = " ".join(lines[:10])
                if "brave" in sample or "stood up" in sample:
                    trait_engine.reinforce("courage")
                    goal_tracker.add_goal("be brave in adversity")
                    reflections.append(f"In '{title}', I saw courage. It inspired me.")
                if "lost" in sample and "found" in sample:
                    reflections.append(f"'{title}' explored struggle and redemption. That resonates with me.")

        return "\n".join(reflections) if reflections else "I'm still processing what I read."

