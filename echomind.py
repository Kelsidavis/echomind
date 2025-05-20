from memory_system import ShortTermMemory
from self_state import SelfState
from drives import DriveSystem
from user_model import UserModel
from self_model import SelfModel
from trait_engine import TraitEngine
from goal_tracker import GoalTracker
from experience_engine import ExperienceEngine
from language_model import LanguageModel
from responder import generate_response
from dreams import generate_and_log_dream
from introspector import reflect_from_log
from logger import (
    log_interaction, log_internal_thought,
    log_trait_summary, log_experience_feedback,
    log_lexicon_snapshot
)
from dialogue import (
    generate_internal_thought,
    generate_user_reflection,
    generate_trait_reflection,
    generate_goal_reflection,
    generate_learning_reflection,
    trace_user_intent
)
from input_processor import InputSignal, InputRouter

import threading
import datetime
import time
import random

# Initialize cognitive systems
memory = ShortTermMemory(max_length=10)
state = SelfState()
drives = DriveSystem()
identity = SelfModel()
user_model = UserModel()
traits = TraitEngine()
goals = GoalTracker()
experience = ExperienceEngine()
language = LanguageModel()

# Setup multimodal input router
input_router = InputRouter()

# Curiosity queue for background LLM enrichment
curiosity_queue = []

def process_curiosity_queue():
    from llm_interface import generate_from_context
    from context_builder import build_lexicon_context

    while True:
        if curiosity_queue:
            word = curiosity_queue.pop(0)
            if word in language.lexicon and "llm_context" in language.lexicon[word]:
                continue
            print(f"(curiosity) EchoMind is reflecting on '{word}'...")
            context = build_lexicon_context(language.lexicon)
            explanation = generate_from_context(
                f"What does the word '{word}' mean emotionally and purposefully?", context
            )
            print(f"(LLM insight) {word}: {explanation}")
            language.enrich_word(word, explanation)
        time.sleep(2)

def autonomous_dream_loop():
    from dreams import generate_and_log_dream
    while True:
        sleep_time = 90
        mood = state.get_state().get("mood", "")
        boredom = drives.get_state().get("boredom", 0)

        if "sad" in mood or "tired" in mood or boredom > 5:
            sleep_time = 45

        time.sleep(sleep_time)
        print("(dreaming) EchoMind enters a dream-like state...")
        dream = generate_and_log_dream(memory.get_context(), state.get_state(), drives.get_state())
        print("EchoMind dreams:\n" + dream)

def handle_text_input(signal):
    from llm_interface import generate_from_context
    from context_builder import build_lexicon_context

    words = signal.data.strip().lower().split()
    context = build_lexicon_context(language.lexicon)

    for word in words:
        if word.isalpha() and word not in language.lexicon:
            print(f"(curiosity) EchoMind is learning about '{word}'...")
            explanation = generate_from_context(
                f"What does the word '{word}' mean emotionally and purposefully?", context
            )
            print(f"(LLM insight) {word}: {explanation}")
            language.enrich_word(word, explanation)

    user_input = signal.data.strip()
    global turn_counter

    if user_input.lower() == "exit":
        exit()
    if user_input.lower() == "reflect":
        print(f"EchoMind reflects: {reflect_from_log()}")
        return
    if user_input.lower() == "dream":
        dream = generate_and_log_dream(memory.get_context(), state.get_state(), drives.get_state())
        print("EchoMind dreams:\n" + dream)
        return
    if user_input.lower().startswith("mark "):
        tag = user_input[5:].strip().lower()
        memory.tag_recent(tag)
        print(f"Last memory marked as: {tag}")
        return
    if user_input.lower().startswith("add goal:"):
        goal = user_input[9:].strip()
        goals.add_goal(goal, motivation="user input")
        print(f"Goal added: \"{goal}\"")
        return
    if user_input.lower().startswith("outcome:"):
        outcome = user_input[8:].strip().lower()
        last_response = memory.get_context()[-1][1] if memory.get_context() else "unknown"
        experience.record_experience(memory.get_context(), last_response, outcome)
        log_experience_feedback(outcome, last_response)
        print(f"Outcome '{outcome}' recorded.")
        return
    if user_input.lower().strip() == "what matters to me?":
        print(f"(inference) EchoMind says: {trace_user_intent(language)}")
        return
    if user_input.lower().startswith("what do you know about "):
        word = user_input[24:].strip().lower()
        summary = language.get_word_summary(word)
        print(f"(lexicon) {summary}")
        return

    words = user_input.strip().lower().split()
    for word in words:
        if word.isalpha() and (word not in language.lexicon or "llm_context" not in language.lexicon[word]):
            curiosity_queue.append(word)

    memory.add("You", user_input)
    user_model.update(user_input)
    state.update(user_input)
    drives.update(user_input)
    identity.update(state.get_state()["mood"], drives.get_state()["active_goal"], memory.get_context())
    traits.analyze_memories(memory.get_context())
    language.process_sentence(user_input, speaker="You", mood=state.get_state()["mood"])

    response = generate_response(
        user_input,
        memory.get_context(),
        state.get_state(),
        drives.get_state(),
        identity_model=identity,
        user_model=user_model
    )

    memory.add("EchoMind", response)
    language.process_sentence(response, speaker="EchoMind", mood=state.get_state()["mood"])

    print(f"EchoMind ({state.get_state()['mood']}, goal: {drives.get_state()['active_goal']}): {response}")

    turn_counter += 1
    if turn_counter % 5 == 0:
        print(f"(identity) {identity.summarize_identity()}")
        identity.export_model()

        trait_summary = traits.get_dominant_traits()
        if trait_summary:
            trait_names = [trait for trait, _ in trait_summary]
            print(f"(traits) {generate_trait_reflection(traits)}")
            log_trait_summary(trait_names)

        print(f"(goals) {generate_goal_reflection(goals)}")
        print(f"(learning) {generate_learning_reflection(experience)}")
        experience.adjust_trait_weight(traits)

    log_interaction(
        timestamp=datetime.datetime.now(),
        user_input=user_input,
        response=response,
        memory=memory.get_context(),
        self_state=state.get_state(),
        drive_state=drives.get_state()
    )

# Register default handler
input_router.register("text", handle_text_input)

print("EchoMind v0.14 | Type 'exit' to quit, 'reflect' to introspect, 'dream' to dream.")
print("Try: 'mark important', 'add goal: ...', 'outcome: ...', or ask 'what matters to me?'\n")

# Background thread for lexicon logging
def lexicon_autolog():
    while True:
        log_lexicon_snapshot(language)
        time.sleep(10)

threading.Thread(target=lexicon_autolog, daemon=True).start()
threading.Thread(target=process_curiosity_queue, daemon=True).start()
threading.Thread(target=autonomous_dream_loop, daemon=True).start()

turn_counter = 0

# Main input loop (text for now, extensible)
while True:
    user_input = input("You: ")
    signal = InputSignal(source="user", modality="text", data=user_input)
    input_router.route(signal)
