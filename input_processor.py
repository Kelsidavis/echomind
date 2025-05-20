from datetime import datetime

class InputSignal:
    def __init__(self, source, modality, data, timestamp=None):
        self.source = source              # e.g., "user", "microphone", "camera"
        self.modality = modality          # e.g., "text", "audio", "image", "sensor"
        self.data = data
        self.timestamp = timestamp or datetime.now()

class InputRouter:
    def __init__(self):
        self.handlers = {}  # modality -> handler function

    def register(self, modality, handler):
        self.handlers[modality] = handler

    def route(self, input_signal):
        handler = self.handlers.get(input_signal.modality)
        if handler:
            handler(input_signal)
        else:
            print(f"No handler for modality '{input_signal.modality}' registered.")
