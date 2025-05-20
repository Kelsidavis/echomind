from memory_system import ShortTermMemory
from self_state import SelfState
from responder import generate_response
from logger import log_interaction
from introspector import reflect_from_log
from drives import DriveSystem
from dreams import generate_and_log_dream

import datetime
import random

memory = ShortTermMemory(max_length=5)
state = SelfState()
drives = DriveSystem()

print("EchoMind v0.5 | Type 'exit' to quit, 'reflect' to introspect, 'dream' to dream.\n")

while True:
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

    if user_input.lower() == "dream":
        dream = generate_and_log_dream(memory.get_context(), state.get_state(), drives.get_state())
        print("EchoMind dreams:\n" + dream)
        continue

    memory.add("You", user_input)
    state.update(user_input)
    drives.update(user_input)
    current_state = state.get_state()
    current_drives = drives.get_state()

    response = generate_response(user_input, memory.get_context(), current_state, current_drives)
    memory.add("EchoMind", response)

    print(f"EchoMind ({current_state['mood']}, goal: {current_drives['active_goal']}): {response}")

    log_interaction(
        timestamp=datetime.datetime.now(),
        user_input=user_input,
        response=response,
        memory=memory.get_context(),
        self_state=current_state,
        drive_state=current_drives
    )
