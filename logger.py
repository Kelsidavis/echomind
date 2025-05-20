import datetime
import threading

log_lock = threading.Lock()

def log_interaction(timestamp, user_input, response, memory, self_state, drive_state):
    """
    Logs a complete interaction including user input, response, internal state, and memory context.
    """
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
    """
    Logs EchoMind's internal monologue and reflections.
    """
    try:
        with log_lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] [THOUGHT] {thought}\n")
    except Exception as e:
        print(f"Internal voice logging error: {e}")

def log_ethics_journal(statement, violated_values, log_path="logs/ethics_journal.log"):
    """
    Logs any value violations for ethical self-monitoring.
    """
    try:
        with log_lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] [VALUES] Statement: {statement}\n")
                f.write(f"[VALUES] Violated Values: {', '.join(violated_values)}\n")
    except Exception as e:
        print(f"Ethics journal logging error: {e}")

def log_trait_summary(traits, path="logs/traits.log"):
    """
    Logs derived long-term personality traits from behavioral patterns.
    """
    try:
        with log_lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] [TRAITS] Trait Summary: {', '.join(traits)}\n")
    except Exception as e:
        print(f"Trait logging error: {e}")

def log_experience_feedback(outcome, response, log_path="logs/experience.log"):
    """
    Logs user interaction outcomes and model feedback.
    """
    try:
        with log_lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] [EXPERIENCE] Outcome: {outcome} | Response: {response}\n")
    except Exception as e:
        print(f"Experience logging error: {e}")

def log_lexicon_snapshot(language_model, path="logs/lexicon.log"):
    """
    Logs the current state of the semantic lexicon, including emotional and contextual tags.
    """
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
