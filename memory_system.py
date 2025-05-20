import time

class MemoryEntry:
    def __init__(self, speaker, message, tag="neutral", ttl=300):
        self.speaker = speaker
        self.message = message
        self.tag = tag
        self.created_at = time.time()
        self.ttl = ttl

    def is_expired(self):
        return (time.time() - self.created_at) > self.ttl and self.tag == "neutral"

    def to_tuple(self):
        return (self.speaker, self.message)


class ShortTermMemory:
    def __init__(self, max_length=10):
        self.buffer = []
        self.max_length = max_length

    def add(self, speaker, message, tag="neutral"):
        entry = MemoryEntry(speaker, message, tag)
        self.buffer.append(entry)
        self.cleanup()
        if len(self.buffer) > self.max_length:
            self.buffer.pop(0)

    def tag_recent(self, tag="important"):
        if self.buffer:
            self.buffer[-1].tag = tag

    def cleanup(self):
        self.buffer = [entry for entry in self.buffer if not entry.is_expired()]

    def get_context(self):
        self.cleanup()
        return [entry.to_tuple() for entry in self.buffer]

    def __len__(self):
        return len(self.buffer)
    
    def promote_important(self, keyword="turning point"):
        """
        Retain only the most impactful memories matching a tag or keyword.
        """
        self.buffer = [entry for entry in self.buffer if keyword in entry.message.lower()]


