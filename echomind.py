from memory import ShortTermMemory
from responder import generate_response
from logger import log_interaction
import datetime

memory = ShortTermMemory(max_length=5)

print("EchoMind v0.1 | Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    memory.add("You", user_input)
    response = generate_response(user_input, memory.get_context())
    memory.add("EchoMind", response)

    print(f"EchoMind: {response}")
    log_interaction(datetime.datetime.now(), user_input, response, memory.get_context())
