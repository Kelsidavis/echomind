from memory_system import ShortTermMemory
from self_state import SelfState
from responder import generate_response
from logger import log_interaction
from introspector import reflect_from_log
from drives import DriveSystem
from dreams import generate_and_log_dream
from dialogue import generate_internal_thought, generate_user_reflection, log_internal_thought
from self_model import SelfModel
from user_model import UserModel

import datetime
import random

# Initialize subsystems
memory = ShortTermMemory(max_length=10)
state = SelfState()
drives = DriveSystem()
identity = SelfModel()
user_model = UserModel()

print("EchoMind v0.8 | Type 'exit' to quit, 'reflect' to introspect, 'dream' to dream.")
print("Also try: 'mark important', 'mark confusing', or 'mark pleasant'\n")

turn_counter = 0

while True:
    # Spontaneous internal thought (about self or user)
    if random.random() < 0.3:
        recent_input = memory.get_context()[-1][1] if memory.get_context() else None
        thought = generate_internal_thought(state.get_state(), drives.get_state(), recent_input)
        print(f"(internal) EchoMind thinks: {thought}")
        log_internal_thought(thought)

    if random.random() < 0.15:
        user_thought = generate_user_reflection(user_model)
        print(f"(internal) EchoMind considers you: {user_thought}")
        log_internal_thought(user_thought)

    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        break

    if user_input.lower() == "reflect":
        reflection = reflect_from_log()
        print(f"EchoMind reflects: {reflection}")
        continue

    if user_input.lower() == "dream":
        dream = generate_and_log_dream(memory.get_context(), state.get_state(), drives.get_state())
        print("EchoMind dreams:\n" + dream)
        continue

    if user_input.lower().startswith("mark "):
        tag = user_input[5:].strip().lower()
        memory.tag_recent(tag)
        print(f"Last memory marked as: {tag}")
        continue

    # Core updates
    memory.add("You", user_input)
    user_model.update(user_input)
    state.update(user_input)
    drives.update(user_input)
    current_state = state.get_state()
    current_drives = drives.get_state()

    # Update self identity model
    identity.update(current_state['mood'], current_drives['active_goal'], memory.get_context())

    # Generate EchoMind's response
    response = generate_response(
        user_input,
        memory.get_context(),
        current_state,
        current_drives,
        identity_model=identity,
        user_model=user_model
    )

    memory.add("EchoMind", response)

    print(f"EchoMind ({current_state['mood']}, goal: {current_drives['active_goal']}): {response}")

    # Periodic self-summary
    turn_counter += 1
    if turn_counter % 5 == 0:
        summary = identity.summarize_identity()
        print(f"(identity) EchoMind reflects on itself: {summary}")
        identity.export_model()

    # Log full interaction
    log_interaction(
        timestamp=datetime.datetime.now(),
        user_input=user_input,
        response=response,
        memory=memory.get_context(),
        self_state=current_state,
        drive_state=current_drives
    )
