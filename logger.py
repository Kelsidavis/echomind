import datetime

def log_interaction(timestamp, user_input, response, memory, self_state, drive_state):
    """
    Logs a complete interaction including user input, response, internal state, and memory context.
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
    Logs EchoMind's internal monologue and reflections.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {thought}\n")
    except Exception as e:
        print(f"Internal voice logging error: {e}")


def log_ethics_journal(statement, violated_values, log_path="logs/ethics_journal.log"):
    """
    Logs any value violations for ethical self-monitoring.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}]\n")
            f.write(f"Statement: {statement}\n")
            f.write(f"Violated Values: {', '.join(violated_values)}\n")
    except Exception as e:
        print(f"Ethics journal logging error: {e}")


def log_trait_summary(traits, path="logs/traits.log"):
    """
    Logs derived long-term personality traits from behavioral patterns.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] Trait Summary: {', '.join(traits)}\n")
    except Exception as e:
        print(f"Trait logging error: {e}")
