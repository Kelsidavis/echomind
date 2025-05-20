import random

def reflect_from_log(log_path="logs/introspection.log"):
    try:
        with open(log_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Extract a recent memory or mood from the log
        memories = [line.strip() for line in lines if line.startswith("  You:") or "Self-State" in line]
        if not memories:
            return "I don't have anything to reflect on yet."

        memory_snippet = random.choice(memories[-10:])
        if "Self-State" in memory_snippet and "'mood':" in memory_snippet:
            try:
                mood = memory_snippet.split("'mood':")[1].split(",")[0].strip().strip("'{} ")
                return f"Earlier, I was feeling {mood}. I wonder why."
            except Exception:
                return "I was feeling something, but I can't quite recall the mood clearly."
        else:
            return f"I recall you said: {memory_snippet[2:]}. That stood out to me."

    except Exception as e:
        return f"I'm having trouble reflecting right now: {str(e)}"
