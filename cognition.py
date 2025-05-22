import threading
import time
import random

from introspector import reflect_from_log
from ebook_memory import EbookMemory
from trait_engine import TraitEngine
from goal_tracker import GoalTracker
from drives import DriveSystem
from self_state import SelfState
from memory_system import ShortTermMemory
from logger import log_internal_thought, log_experience_feedback, log_lexicon_snapshot
from experience_engine import ExperienceEngine
from self_model import SelfModel
from semantic_lexicon import LanguageModel
from dialogue import trace_user_intent
from context_builder import build_lexicon_context
from llm_interface import generate_from_context
from dreams import generate_and_log_dream
from activity_state import set_activity

# Shared instances
memory = ShortTermMemory(max_length=10)
state = SelfState()
drives = DriveSystem()
goals = GoalTracker()
traits = TraitEngine()
experience = ExperienceEngine()
identity = SelfModel()
language = LanguageModel()

curiosity_queue = []

def automatic_reflection_loop():
    while True:
        time.sleep(180)
        mood = state.get_state().get("mood", "")
        if "tired" in mood or "sad" in mood or random.random() < 0.3:
            print("(reflection) EchoMind reflects:", reflect_from_log())

def automatic_book_reflection_loop():
    while True:
        time.sleep(300)
        ebook_memory = EbookMemory()
        thoughts = ebook_memory.reflect_on_books(traits, goals)
        log_internal_thought(f"[BOOK REFLECTION] {thoughts}")
        print(f"(book) EchoMind reflected on reading:\n{thoughts}")

def automatic_value_introspection_loop():
    while True:
        time.sleep(240)
        print("(introspection) EchoMind considers what matters...")
        print("(inference)", trace_user_intent(language))

def automatic_memory_tagging():
    while True:
        time.sleep(60)
        last = memory.get_context()[-1] if memory.get_context() else None
        if last and any(kw in last[1].lower() for kw in ["remember", "important", "note this"]):
            memory.tag_recent("important")
            print("(memory) Tagged last memory as important")

def process_curiosity_queue():
    while True:
        if curiosity_queue:
            word = curiosity_queue.pop(0)
            if word in language.lexicon and "llm_context" in language.lexicon[word]:
                continue
            set_activity("Reflecting")
            print(f"(curiosity) EchoMind is reflecting on '{word}'...")
            context = build_lexicon_context(language.lexicon)
            explanation = generate_from_context(
                f"What does the word '{word}' mean emotionally and purposefully?", context
            )
            print(f"(LLM insight) {word}: {explanation}")
            language.enrich_word(word, explanation)
        time.sleep(2)
        set_activity("Idle")

def autonomous_dream_loop():
    while True:
        sleep_time = 90
        mood = state.get_state().get("mood", "")
        boredom = drives.get_state().get("boredom", 0)
        if "sad" in mood or "tired" in mood or boredom > 5:
            sleep_time = 45
        time.sleep(sleep_time)
        set_activity("Dreaming")
        print("(dreaming) EchoMind enters a dream-like state...")
        dream = generate_and_log_dream(memory.get_context(), state.get_state(), drives.get_state())
        print("EchoMind dreams:\n" + dream)
        time.sleep(2)
        set_activity("Idle")

def autonomous_initiation_loop():
    while True:
        time.sleep(random.randint(60, 180))
        current_mood = state.get_state().get("mood", "neutral")
        current_energy = state.get_state().get("energy", 100)
        boredom = drives.get_state().get("boredom", 0)
        if current_energy < 40:
            continue
        if random.random() < 0.4:
            prompt = "Ask the user a question out of curiosity."
            tag = "QUESTION"
        else:
            prompt = "Say something spontaneously to start a conversation or reflect aloud."
            tag = "THOUGHT"
        context = build_lexicon_context(language.lexicon)
        thought = generate_from_context(prompt, context, context_type="default")
        memory.add("EchoMind", thought)
        language.process_sentence(thought, speaker="EchoMind", mood=current_mood)
        log_internal_thought(f"[{tag}] {thought}")
        print(f"(unsolicited) EchoMind: {thought}")

def lexicon_autolog():
    while True:
        log_lexicon_snapshot(language)
        time.sleep(10)

def launch_background_cognition():
    threading.Thread(target=autonomous_initiation_loop, daemon=True).start()
    threading.Thread(target=lexicon_autolog, daemon=True).start()
    threading.Thread(target=process_curiosity_queue, daemon=True).start()
    threading.Thread(target=autonomous_dream_loop, daemon=True).start()
    threading.Thread(target=automatic_reflection_loop, daemon=True).start()
    threading.Thread(target=automatic_value_introspection_loop, daemon=True).start()
    threading.Thread(target=automatic_memory_tagging, daemon=True).start()
    threading.Thread(target=automatic_book_reflection_loop, daemon=True).start()
