import threading
import traceback

class TaskRunner:
    def __init__(self):
        self.threads = {}

    def run(self, name, target, args=(), daemon=True):
        """Starts a named thread for a background task."""
        if name in self.threads and self.threads[name].is_alive():
            return  # Already running

        def safe_wrapper():
            try:
                target(*args)
            except Exception:
                traceback.print_exc()

        t = threading.Thread(target=safe_wrapper, daemon=daemon)
        self.threads[name] = t
        t.start()

    def is_running(self, name):
        return name in self.threads and self.threads[name].is_alive()

    def stop_all(self):
        self.threads.clear()  # Threads are daemonic, so they'll end with the process
