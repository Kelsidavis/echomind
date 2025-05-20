def log_interaction(timestamp, user_input, response, memory, self_state):
    with open("logs/introspection.log", "a") as log_file:
        log_file.write(f"\n[{timestamp}]\n")
        log_file.write(f"User: {user_input}\n")
        log_file.write(f"EchoMind: {response}\n")
        log_file.write("Self-State: " + str(self_state) + "\n")
        log_file.write("Memory Context:\n")
        for speaker, message in memory:
            log_file.write(f"  {speaker}: {message}\n")
