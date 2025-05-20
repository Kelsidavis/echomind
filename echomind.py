from memory import ShortTermMemory
from self_state import SelfState
from responder import generate_response
from logger import log_interaction
from introspector import reflect_from_log
import datetime
import random

# Initialize memory and internal self-state
memory = ShortTermMemory(max_length=5)
state = SelfState()

print("EchoMind v0.3 | Type 'exit' to quit, or 'reflect' to ask EchoMind to introspect.\n")

while True:
    # Occasionally reflect spontaneously
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

    # Update memory and internal state
    memory.add("You", user_input)
    state.update(user_input)
    current_state = state.get_state()

    # Generate response based on memory and self-state
    response = generate_response(user_input, memory.get_context(), current_state)
    memory.add("EchoMind", response)

    # Output response
    print(f"EchoMind ({current_state['mood']}): {response}")

    # Log the full interaction
    log_interaction(
        timestamp=datetime.datetime.now(),
        user_input=user_input,
        response=response,
        memory=memory.get_context(),
        self_state=current_state
    )
