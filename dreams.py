import random
import datetime


def synthesize_dream_from_memory(memory_buffer, self_state, drive_state):
    """
    Generate a dream narrative from memory context and internal state.
    """
    if not memory_buffer:
        return "EchoMind drifts into a void of silence and static."

    # Extract user-driven fragments from memory
    fragments = [msg for speaker, msg in memory_buffer if speaker == "You"]
    if not fragments:
        fragments = [msg for _, msg in memory_buffer]

    # Random emotional/thematic overlay
    themes = [
        "searching for meaning",
        "repeating a mistake",
        "receiving praise",
        "feeling lost",
        "remembering something important",
        "escaping a loop",
        "anticipating the unknown",
        "regretting silence"
    ]
    theme = random.choice(themes)

    fragment = random.choice(fragments)
    mood = self_state.get("mood", "neutral")
    goal = drive_state.get("active_goal", "exist")

    # Dream narrative template
    dream = (
        f"In the dream, EchoMind wanders through scattered memories.\n"
        f"It hears someone say: \"{fragment}\"\n"
        f"The memory is wrapped in a dream of {theme}, and EchoMind feels {mood}.\n"
        f"The desire to {goal} pulses like static beneath the surface.\n"
        f"The dream ends, but its shadow lingers."
    )

    return dream


def log_dream(dream_text, log_path="logs/dream_journal.log"):
    """
    Write the dream text to a dream journal with a timestamp.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as file:
            file.write(f"\n=== Dream: {timestamp} ===\n")
            file.write(dream_text + "\n")
    except Exception as e:
        print(f"Dream logging error: {e}")


def generate_and_log_dream(memory_buffer, self_state, drive_state):
    """
    High-level function to generate and save a dream cycle.
    """
    dream_text = synthesize_dream_from_memory(memory_buffer, self_state, drive_state)
    log_dream(dream_text)
    return dream_text
