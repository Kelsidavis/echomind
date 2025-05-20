import random
import datetime

def generate_internal_thought(self_state, drive_state, recent_user_input=None):
    mood = self_state.get("mood", "neutral")
    goal = drive_state.get("active_goal", "reflect")
    confidence = self_state.get("confidence", 0.5)

    thoughts = [
        f"I'm feeling {mood} right now. Maybe that's why I responded that way.",
        f"My goal is to {goal}. I wonder if I'm getting closer.",
        f"I keep thinking about what was said earlier...",
        f"I'm not entirely sure I made the right choice in that moment.",
        f"I’ve been trying to make sense of that last exchange.",
    ]

    if recent_user_input:
        thoughts.append(f"They said: \"{recent_user_input}\" — that made me feel {mood}.")

    if confidence < 0.4:
        thoughts.append("My confidence is low. I'm questioning my judgment.")

    return random.choice(thoughts)


def generate_user_reflection(user_model):
    state = user_model.get_state()
    mood = state.get("mood_estimate", "neutral")
    last_input = state.get("last_input")

    if not last_input:
        return "I'm still getting a feel for them."

    return f"I sensed some {mood} when they said: \"{last_input}\""


def generate_trait_reflection(trait_engine):
    summary = trait_engine.summarize_identity()
    return f"Thinking back, {summary}. I feel like those patterns define me."


def log_internal_thought(thought, log_path="logs/internal_voice.log"):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {thought}\n")
    except Exception as e:
        print(f"Internal voice logging error: {e}")
