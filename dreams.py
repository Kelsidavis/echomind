import random
import datetime
from textblob import TextBlob
from trait_engine import TraitEngine

traits = TraitEngine()  # Use the shared global instance in your main script if needed

THEME_TRAIT_MAP = {
    "loop": {"curiosity": +1, "patience": -1},
    "static": {"engagement": +1},
    "escape": {"freedom": +1},
    "laboratory": {"logic": +1, "risk-taking": +1},
    "mistake": {"reflection": +1, "impulsivity": -1},
    "unknown": {"exploration": +1},
    "silence": {"introspection": +1},
    "praise": {"confidence": +1},
    "lost": {"resilience": +1, "confidence": -1}
}

def score_emotion(text):
    """
    Analyze sentiment of dream text and assign a mood label.
    """
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.3:
        return "uplifted"
    elif polarity < -0.3:
        return "disturbed"
    else:
        return "neutral"

def extract_themes(dream_text):
    """
    Detect dream themes based on keywords in the text.
    """
    themes = []
    for key in THEME_TRAIT_MAP:
        if key in dream_text.lower():
            themes.append(key)
    return themes

def apply_trait_changes(themes):
    """
    Modify traits based on detected dream themes.
    """
    for theme in themes:
        trait_changes = THEME_TRAIT_MAP.get(theme, {})
        for trait, delta in trait_changes.items():
            traits.trait_counts[trait] += delta
            traits.trait_log.append([f"Dream-adjusted {trait} by {delta} due to {theme}"])

def log_dream_entry(dream_text, mood, themes, log_path="logs/dreams.log"):
    """
    Write formatted dream log with metadata.
    """
    timestamp = datetime.datetime.now().isoformat()
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- Dream @ {timestamp} ---\n")
            f.write(f"Mood: {mood}\n")
            f.write(f"Themes: {', '.join(themes) if themes else 'none'}\n")
            f.write("Content:\n" + dream_text + "\n")
            f.write(f"-----------------------------\n")
    except Exception as e:
        print(f"Dream logging error: {e}")

def synthesize_dream_from_memory(memory_buffer, self_state, drive_state):
    """
    Generate a dream narrative from memory context and internal state.
    """
    if not memory_buffer:
        return "EchoMind drifts into a void of silence and static."

    # Extract user-driven fragments from memory
    fragments = [msg for speaker, msg in memory_buffer if speaker == "You" and len(msg.split()) > 3 and not msg.strip().startswith("print(")]
    if not fragments:
        fragments = [msg for _, msg in memory_buffer]

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

    mood = score_emotion(dream_text)
    self_state["mood"] = mood
    goal = drive_state.get("active_goal", "exist")

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
    Legacy dream log (simple, kept for compatibility).
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
    High-level function to generate, score, analyze, and save a dream cycle.
    """
    dream_text = synthesize_dream_from_memory(memory_buffer, self_state, drive_state)
    mood = score_emotion(dream_text)
    self_state["mood"] = mood  # Optional: set new mood based on dream
    themes = extract_themes(dream_text)
    apply_trait_changes(themes)
    log_dream(dream_text)
    log_dream_entry(dream_text, mood, themes)
    return dream_text
