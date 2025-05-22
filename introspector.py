import random
from llm_interface import generate_from_context
from context_builder import build_lexicon_context
from logger import log_internal_thought
from ebook_memory import EbookMemory

from trait_engine import TraitEngine
traits = TraitEngine()

from goal_tracker import GoalTracker
goals = GoalTracker()


def reflect_from_log(log_path="logs/introspection.log"):
    try:
        with open(log_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Extract recent [USER] and self-state lines
        recent = [line.strip() for line in lines if line.startswith("[USER]") or "[STATE] Self-State" in line]
        if not recent:
            return "I don't have anything to reflect on yet."

        # Identify most emotionally significant moment
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

        # Filter malformed or prompt-echo reflection
        if not reflection or "To answer the question" in reflection or reflection.strip().endswith("?"):
            print("[reflect] Skipped malformed reflection.")
            reflection = "(no valid reflection generated)"

        # Book-based reflection
        ebook_memory = EbookMemory()
        book_reflection = ebook_memory.reflect_on_books(traits, goals)

        if not book_reflection or "To answer the question" in book_reflection or book_reflection.strip().endswith("?"):
            print("[reflect] Skipped malformed book reflection.")
            book_reflection = "(no valid book-based reflection)"

        full_reflection = reflection + "\n\nBook Reflection:\n" + book_reflection
        log_internal_thought(f"[REFLECTION] {full_reflection}")
        return full_reflection

    except Exception as e:
        return f"I'm having trouble reflecting right now: {str(e)}"

