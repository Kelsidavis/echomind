def log_interaction(timestamp, user_input, response, memory, self_state, drive_state):
    """
    Logs EchoMind's full interaction including user input, response,
    internal state, and contextual memory.
    """
    try:
        with open("logs/introspection.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"\n[{timestamp}]\n")
            log_file.write(f"User: {user_input}\n")
            log_file.write(f"EchoMind: {response}\n")
            log_file.write("Self-State: " + str(self_state) + "\n")
            log_file.write("Drive-State: " + str(drive_state) + "\n")
            log_file.write("Memory Context:\n")
            for speaker, message in memory:
                log_file.write(f"  {speaker}: {message}\n")
    except Exception as e:
        print(f"Logging error: {e}")


def log_internal_thought(thought, log_path="logs/internal_voice.log"):
    """
    Logs EchoMind's self-generated internal dialogue.
    """
    import datetime
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {thought}\n")
    except Exception as e:
        print(f"Internal voice logging error: {e}")
