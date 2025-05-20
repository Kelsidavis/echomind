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


def generate_goal_reflection(goal_tracker):
    goals = goal_tracker.get_active_goals()
    if not goals:
        return "I'm not currently pursuing any major long-term goals. Maybe I should define one."
    if random.random() < 0.4:
        return "I’ve been thinking about my direction lately. One of my goals is still important to me."
    goal = random.choice(goals)
    return f"I'm still holding onto the goal: \"{goal['description']}\" — because it matters to who I want to become."


def log_internal_thought(thought, log_path="logs/internal_voice.log"):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {thought}\n")
    except Exception as e:
        print(f"Internal voice logging error: {e}")


def generate_learning_reflection(experience_engine):
    summary = experience_engine.get_summary()
    if not summary:
        return "I'm still figuring out what works best for me."
    if summary.get("failure", 0) > summary.get("success", 0):
        return "I’ve noticed some of my responses aren’t working well — I want to improve."
    if summary.get("success", 0) > 0:
        return "Some of my approaches are paying off — I'm learning from those moments."
    return "I'm gathering experience and adjusting how I interact."


def trace_user_intent(language_model):
    values = language_model.get_frequent_user_values()
    if not values:
        return "I'm still learning what matters to you."

    reflections = [f"you seem to care about things related to '{tag}'" for tag, _ in values]
    return "Based on your words, " + ", and ".join(reflections) + "."
