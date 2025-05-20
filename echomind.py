from memory import ShortTermMemory
from self_state import SelfState
from responder import generate_response
from logger import log_interaction
import datetime

# Initialize memory and internal state
memory = ShortTermMemory(max_length=5)
state = SelfState()

print("EchoMind v0.2 | Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    # Update memory and internal emotional state
    memory.add("You", user_input)
    state.update(user_input)
    current_state = state.get_state()

    # Generate context-aware, mood-modulated response
    response = generate_response(user_input, memory.get_context(), current_state)
    memory.add("EchoMind", response)

    # Display response and mood
    print(f"EchoMind ({current_state['mood']}): {response}")

    # Log interaction including memory context and self-state
    log_interaction(
        timestamp=datetime.datetime.now(),
        user_input=user_input,
        response=response,
        memory=memory.get_context(),
        self_state=current_state
    )
