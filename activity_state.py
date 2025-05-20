# activity_state.py
import threading

_lock = threading.Lock()
_current = "Idle"

def set_activity(activity: str):
    global _current
    with _lock:
        _current = activity

def get_activity():
    with _lock:
        return _current
