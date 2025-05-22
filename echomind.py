from memory_system import ShortTermMemory
from self_state import SelfState
from drives import DriveSystem
from user_model import UserModel
from self_model import SelfModel
from trait_engine import TraitEngine
from goal_tracker import GoalTracker
from experience_engine import ExperienceEngine
from semantic_lexicon import LanguageModel
from responder import generate_response
from dreams import generate_and_log_dream
from introspector import reflect_from_log
from logger import (
    ensure_log_files_exist,
    log_startup_message,
    log_interaction,
    log_internal_thought,
    log_trait_summary,
    log_experience_feedback,
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
from activity_state import set_activity
from mind_gui import gui_ref

# Set up logging
ensure_log_files_exist()
log_startup_message()

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

# === Automation Threads ===

def automatic_reflection_loop():
    from introspector import reflect_from_log
    while True:
        time.sleep(180)
        mood = state.get_state().get("mood", "")
        if "tired" in mood or "sad" in mood or random.random() < 0.3:
            print("(reflection) EchoMind reflects:", reflect_from_log())

def automatic_value_introspection_loop():
    from dialogue import trace_user_intent
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

def automatic_outcome_inference(user_input):
    outcome_map = {
        "worked": "success",
        "succeeded": "success",
        "glad": "success",
        "happy": "success",
        "failed": "failure",
        "didn't work": "failure",
        "regret": "failure",
        "angry": "failure"
    }
    for phrase, outcome in outcome_map.items():
        if phrase in user_input.lower():
            last_response = memory.get_context()[-1][1] if memory.get_context() else "unknown"
            experience.record_experience(memory.get_context(), last_response, outcome)
            log_experience_feedback(outcome, last_response)
            print(f"(experience) Inferred and recorded outcome: {outcome}")
            break

def detect_goal_statement(user_input):
    triggers = ["i want to", "i will", "my goal is", "i plan to"]
    for t in triggers:
        if t in user_input.lower():
            goal_text = user_input[user_input.lower().find(t):]
            goals.add_goal(goal_text, motivation="inferred")
            print(f"(goal) Inferred and added goal: '{goal_text}'")
            break

# === Curiosity Enrichment ===

curiosity_queue = []

def process_curiosity_queue():
    from llm_interface import generate_from_context
    from context_builder import build_lexicon_context

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

# === Autonomous Dreaming ===

def autonomous_dream_loop():
    from dreams import generate_and_log_dream
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
        
# === Speak Freely ===

def autonomous_initiation_loop():
    import random
    while True:
        time.sleep(random.randint(60, 180))  # Occasional behavior
        current_mood = state.get_state().get("mood", "neutral")
        current_energy = state.get_state().get("energy", 100)
        boredom = drives.get_state().get("boredom", 0)

        # Only speak if EchoMind is alert enough
        if current_energy < 40:
            continue

        from context_builder import build_lexicon_context
        context = build_lexicon_context(language.lexicon)

        # Curiosity or unsolicited thought
        if random.random() < 0.4:
            prompt = "Ask the user a question out of curiosity."
            tag = "QUESTION"
        else:
            prompt = "Say something spontaneously to start a conversation or reflect aloud."
            tag = "THOUGHT"

        thought = generate_from_context(prompt, context, context_type="default")

        memory.add("EchoMind", thought)
        language.process_sentence(thought, speaker="EchoMind", mood=current_mood)
        log_internal_thought(f"[{tag}] {thought}")
        print(f"(unsolicited) EchoMind: {thought}")

        # If GUI is active, append to it
        try:
            if gui_ref:
                gui_ref.append_log(tag, thought)
        except NameError:
            pass  # GUI not connected
            

# === Input Handler ===

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
    
    memory.add("You", user_input)  # <-- Moved before generation


    detect_goal_statement(user_input)
    automatic_outcome_inference(user_input)

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

    if user_input.lower().startswith("read "):
        filepath = user_input[5:].strip()
        signal = InputSignal(source="user", modality="text_corpus", data=filepath)
        input_router.route(signal)
        return

    for word in words:
        if word.isalpha() and (word not in language.lexicon or "llm_context" not in language.lexicon[word]):
            curiosity_queue.append(word)

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
        user_model=user_model,
        semantic_lexicon=language,
        trait_engine=traits
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

# text corpus handler
from input_processor import handle_text_corpus
input_router.register("text_corpus", lambda signal: handle_text_corpus(signal, memory, language))

print("EchoMind v0.14 | Type 'exit' to quit, 'reflect' to introspect, 'dream' to dream.")
print("Try: 'mark important', 'add goal: ...', 'outcome: ...', or ask 'what matters to me?'\n")

def lexicon_autolog():
    while True:
        log_lexicon_snapshot(language)
        time.sleep(10)

threading.Thread(target=autonomous_initiation_loop, daemon=True).start()
threading.Thread(target=lexicon_autolog, daemon=True).start()
threading.Thread(target=process_curiosity_queue, daemon=True).start()
threading.Thread(target=autonomous_dream_loop, daemon=True).start()
threading.Thread(target=automatic_reflection_loop, daemon=True).start()
threading.Thread(target=automatic_value_introspection_loop, daemon=True).start()
threading.Thread(target=automatic_memory_tagging, daemon=True).start()

turn_counter = 0

from mind_gui import launch_dashboard
from threading import Thread

#Thread(target=lambda: launch_dashboard(router=input_router), daemon=True).start()
launch_dashboard(router=input_router)


# for gui use comment this out
#while True:
#    user_input = input("You: ")
#    signal = InputSignal(source="user", modality="text", data=user_input)
#    input_router.route(signal)
