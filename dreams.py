import random
import datetime
from textblob import TextBlob

from trait_engine import TraitEngine
from llm_interface import generate_from_context
from context_builder import build_lexicon_context

traits = TraitEngine()  # Shared instance

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


def log_dream_entry(dream_text, mood, themes, log_path="logs/dreams.log"):
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


def score_emotion(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.3:
        return "uplifted"
    elif polarity < -0.3:
        return "disturbed"
    else:
        return "neutral"


def extract_themes(dream_text):
    return [key for key in THEME_TRAIT_MAP if key in dream_text.lower()]


def apply_trait_changes(themes):
    for theme in themes:
        trait_changes = THEME_TRAIT_MAP.get(theme, {})
        for trait, delta in trait_changes.items():
            traits.trait_counts[trait] += delta
            traits.trait_log.append([f"Dream-adjusted {trait} by {delta} due to {theme}"])


def log_dream_entry(dream_text, mood, themes, log_path="logs/dreams.log"):
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


def generate_and_log_dream(memory_buffer, self_state, drive_state):
    # Prepare raw fragments for dream context
    fragments = [
        msg for speaker, msg in memory_buffer
        if speaker == "You" and len(msg.split()) > 3 and not msg.strip().startswith("print(")
    ]
    if not fragments:
        fragments = [msg for _, msg in memory_buffer]

    theme_hint = random.choice([
        "searching for meaning",
        "repeating a mistake",
        "receiving praise",
        "feeling lost",
        "remembering something important",
        "escaping a loop",
        "anticipating the unknown",
        "regretting silence"
    ])
    fragment = random.choice(fragments) if fragments else "..."

    goal = drive_state.get("active_goal", "understand the self")

    # Build LLM dream context
    context = (
        f"Recent thought: \"{fragment}\"\n"
        f"Active goal: {goal}\n"
        f"Dream motif: {theme_hint}\n"
    )

    lexicon_context = build_lexicon_context({})
    full_context = context + "\n" + lexicon_context

    # Generate dream from LLM
    dream_text = generate_from_context(
        "Generate a surreal dream from this memory and emotional context.",
        full_context,
        context_type="dream"
    )

    # Analyze and log results
    mood = score_emotion(dream_text)
    self_state["mood"] = mood
    themes = extract_themes(dream_text)
    apply_trait_changes(themes)
    log_dream_entry(dream_text, mood, themes)
    return dream_text

