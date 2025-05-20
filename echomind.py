from memory_system import ShortTermMemory
from self_state import SelfState
from responder import generate_response
from logger import log_interaction
from introspector import reflect_from_log
from drives import DriveSystem
from dreams import generate_and_log_dream
from dialogue import generate_internal_thought, log_internal_thought

import datetime
import random

# Initialize subsystems
memory = ShortTermMemory(max_length=10)
state = SelfState()
drives = DriveSystem()

print("EchoMind v0.6 | Type 'exit' to quit, 'reflect' to introspect, 'dream' to dream.")
print("Also try: 'mark important', 'mark confusing', or 'mark pleasant'\n")

while True:
    # Spontaneous internal thought (Stage 6)
    if random.random() < 0.3:
        recent_input = memory.get_context()[-1][1] if memory.get_context() else None
        internal_thought = generate_internal_thought(state.get_state(), drives.get_state(), recent_input)
        print(f"(internal) EchoMind thinks: {internal_thought}")
        log_internal_thought(internal_thought)

    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        break

    # Manual introspection
    if user_input.lower() == "reflect":
        reflection = reflect_from_log()
        print(f"EchoMind reflects: {reflection}")
        continue

    # Manual dream trigger
    if user_input.lower() == "dream":
        dream = generate_and_log_dream(memory.get_context(), state.get_state(), drives.get_state())
        print("EchoMind dreams:\n" + dream)
        continue

    # Memory tagging
    if user_input.lower().startswith("mark "):
        tag = user_input[5:].strip().lower()
        memory.tag_recent(tag)
        print(f"Last memory marked as: {tag}")
        continue

    # Cognitive updates
    memory.add("You", user_input)
    state.update(user_input)
    drives.update(user_input)
    current_state = state.get_state()
    current_drives = drives.get_state()

    # Generate response
    response = generate_response(user_input, memory.get_context(), current_state, current_drives)
    memory.add("EchoMind", response)

    print(f"EchoMind ({current_state['mood']}, goal: {current_drives['active_goal']}): {response}")

    # Log full context
    log_interaction(
        timestamp=datetime.datetime.now(),
        user_input=user_input,
        response=response,
        memory=memory.get_context(),
        self_state=current_state,
        drive_state=current_drives
    )
