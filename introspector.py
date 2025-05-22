import random
from llm_interface import generate_from_context
from context_builder import build_lexicon_context
from logger import log_internal_thought

def reflect_from_log(log_path="logs/introspection.log"):
    try:
        with open(log_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Extract recent [USER] and self-state lines
        recent = [line.strip() for line in lines if line.startswith("[USER]") or "[STATE] Self-State" in line]
        if not recent:
            return "I don't have anything to reflect on yet."

        # Identify most emotionally significant moment (heuristic: longest line or containing emotion keywords)
        keywords = ["important", "regret", "happy", "angry", "goal", "fail", "love", "hate"]
        ranked = sorted(recent[-15:], key=lambda x: (any(k in x.lower() for k in keywords), len(x)), reverse=True)
        significant = ranked[0] if ranked else recent[-1]

        # Build context
        sample = "\n".join(recent[-10:])
        lexicon_context = build_lexicon_context({})
        context = f"Recent log:\n{sample}\n\nMost emotionally significant moment:\n{significant}\n\n{lexicon_context}"

        reflection = generate_from_context(
            "Reflect on recent experiences. Identify emotional patterns and consider how they relate to goals.",
            context,
            context_type="reflection"
        )

        log_internal_thought(f"[REFLECTION] {reflection}")
        return reflection

    except Exception as e:
        return f"I'm having trouble reflecting right now: {str(e)}"

