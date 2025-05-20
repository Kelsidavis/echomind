from memory import ShortTermMemory
from self_state import SelfState
from responder import generate_response
from logger import log_interaction
from introspector import reflect_from_log
import datetime
import random

# NEW in Stage 4
from drives import DriveSystem

memory = ShortTermMemory(max_length=5)
state = SelfState()
drives = DriveSystem()

print("EchoMind v0.4 | Type 'exit' to quit, or 'reflect' to introspect.\n")

while True:
    # Periodic introspection
    if random.random() < 0.2:
        reflection = reflect_from_log()
        print(f"EchoMind reflects: {reflection}")

    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    if user_input.lower() == "reflect":
        reflection = reflect_from_log()
        print(f"EchoMind reflects: {reflection}")
        continue

    # Update systems
    memory.add("You", user_input)
    state.update(user_input)
    drives.update(user_input)
    current_state = state.get_state()
    current_drives = drives.get_state()

    # Generate context-aware response
    response = generate_response(user_input, memory.get_context(), current_state, current_drives)
    memory.add("EchoMind", response)

    # Show mood + drive summary in response
    print(f"EchoMind ({current_state['mood']}, goal: {current_drives['active_goal']}): {response}")

    # Log full interaction
    log_interaction(
        timestamp=datetime.datetime.now(),
        user_input=user_input,
        response=response,
        memory=memory.get_context(),
        self_state=current_state,
        drive_state=current_drives
    )
