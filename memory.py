class ShortTermMemory:
    def __init__(self, max_length=5):
        self.buffer = []
        self.max_length = max_length

    def add(self, speaker, message):
        self.buffer.append((speaker, message))
        if len(self.buffer) > self.max_length:
            self.buffer.pop(0)

    def get_context(self):
        return self.buffer.copy()
