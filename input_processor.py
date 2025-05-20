from datetime import datetime
import os

class InputSignal:
    def __init__(self, source, modality, data, timestamp=None):
        self.source = source              # e.g., "user", "microphone", "camera", "file"
        self.modality = modality          # e.g., "text", "audio", "image", "sensor", "text_corpus"
        self.data = data                  # Raw input data or filepath
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
            print(f"[InputRouter] No handler for modality '{input_signal.modality}' registered.")

# --- Text Corpus Support (eBook, Articles, etc.) ---

def ingest_text_file(filepath, chunk_size=500):
    """Read a text file and return a list of chunked strings."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def handle_text_corpus(signal, memory, language):
    """
    Process a large text file as external input to memory and semantic lexicon.
    """
    filepath = signal.data
    if not os.path.isfile(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return

    print(f"[Ingesting] Reading '{filepath}' into EchoMind's context...")

    chunks = ingest_text_file(filepath)
    for chunk in chunks:
        memory.add("Book", chunk, tag="literary")
        language.process_sentence(chunk, speaker="Book")

    print(f"[Ingesting Complete] {len(chunks)} chunks processed from '{os.path.basename(filepath)}'")
