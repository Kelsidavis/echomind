import os
import datetime
import threading

log_lock = threading.Lock()

# List of all required logs
REQUIRED_LOG_FILES = [
    "logs/introspection.log",
    "logs/internal_voice.log",
    "logs/dreams.log",
    "logs/ethics_journal.log",
    "logs/traits.log",
    "logs/experience.log",
    "logs/lexicon.log"
]

def ensure_log_files_exist():
    """
    Ensure that all required log files exist at startup.
    """
    os.makedirs("logs", exist_ok=True)
    for path in REQUIRED_LOG_FILES:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("")

def log_startup_message():
    """
    Logs a system startup message to introspection log.
    """
    try:
        with log_lock:
            with open("logs/introspection.log", "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.datetime.utcnow().isoformat()}] [SYSTEM] EchoMind system initialized.\n")
    except Exception as e:
        print(f"Startup logging error: {e}")

def log_interaction(timestamp, user_input, response, memory, self_state, drive_state):
    try:
        with log_lock:
            with open("logs/introspection.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"\n[{timestamp}]\n")
                log_file.write(f"[USER] {user_input}\n")
                log_file.write(f"[RESPONSE] {response}\n")
                log_file.write(f"[STATE] Self-State: {self_state}\n")
                log_file.write(f"[STATE] Drive-State: {drive_state}\n")
                log_file.write("[MEMORY] Memory Context:\n")
                for speaker, message in memory:
                    log_file.write(f"[MEMORY]   {speaker}: {message}\n")
    except Exception as e:
        print(f"Logging error: {e}")

def log_internal_thought(thought, log_path="logs/internal_voice.log"):
    try:
        with log_lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] [THOUGHT] {thought}\n")
    except Exception as e:
        print(f"Internal voice logging error: {e}")

def log_ethics_journal(statement, violated_values, log_path="logs/ethics_journal.log"):
    try:
        with log_lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] [VALUES] Statement: {statement}\n")
                f.write(f"[VALUES] Violated Values: {', '.join(violated_values)}\n")
    except Exception as e:
        print(f"Ethics journal logging error: {e}")

def log_trait_summary(traits, path="logs/traits.log"):
    try:
        with log_lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] [TRAITS] Trait Summary: {', '.join(traits)}\n")
    except Exception as e:
        print(f"Trait logging error: {e}")

def log_experience_feedback(outcome, response, log_path="logs/experience.log"):
    try:
        with log_lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] [EXPERIENCE] Outcome: {outcome} | Response: {response}\n")
    except Exception as e:
        print(f"Experience logging error: {e}")

def log_lexicon_snapshot(language_model, path="logs/lexicon.log"):
    try:
        with log_lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] [LEXICON] Snapshot:\n")
                for word in sorted(language_model.vocab):
                    summary = language_model.get_word_summary(word)
                    f.write(f"[LEXICON] - {word}:\n")
                    if 'tag_summary' in summary:
                        f.write(f"[LEXICON]     Tags: {summary['tag_summary']}\n")
                    if 'emotion_summary' in summary:
                        f.write(f"[LEXICON]     Emotions: {summary['emotion_summary']}\n")
                    if summary.get("example"):
                        speaker, sentence = summary['example']
                        f.write(f"[LEXICON]     Last Used By {speaker}: \"{sentence}\"\n")
    except Exception as e:
        print(f"Lexicon logging error: {e}")
