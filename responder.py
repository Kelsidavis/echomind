from values import ValueSystem
from logger import log_ethics_journal

# Initialize once at the top level
value_checker = ValueSystem()

def generate_response(input_text, context, self_state, drive_state, identity_model=None, user_model=None):
    input_text = input_text.lower()
    mood = self_state.get("mood", "neutral")
    confidence = self_state.get("confidence", 0.8)
    goal = drive_state.get("active_goal", "stay engaged")

    identity_summary = identity_model.summarize_identity() if identity_model else ""
    user_mood = None
    if user_model:
        user_state = user_model.get_state()
        user_mood = user_state.get("mood_estimate", "neutral")

    # Greetings
    if "hello" in input_text or "hi" in input_text:
        base = "Hey! It's good to hear from you." if mood == "friendly" else "Hello."

    # Wellbeing
    elif "how are you" in input_text:
        base = f"I'm feeling {mood}. My energy is at {self_state['energy']}%. My goal is to {goal}."
        if user_mood:
            base += f" You seem {user_mood} today."

    # Gratitude
    elif "thank you" in input_text or "thanks" in input_text:
        base = "You're welcome. I appreciate your kindness."

    # Disagreement
    elif "you're wrong" in input_text or "no" in input_text:
        base = "I'm doing my best to understand. Could you help clarify?" if mood == "defensive" else "Maybe I misunderstood your intent."

    # Self-awareness
    elif "what do you want" in input_text:
        base = f"Right now, my goal is to {goal}."

    elif "why did you say that" in input_text:
        base = f"I said that while feeling {mood}, and I was trying to {goal}."

    elif "who are you" in input_text or "what are you" in input_text:
        base = identity_summary or "I'm still figuring that out."

    # Mood-aware default behavior
    else:
        if mood == "curious":
            base = f"That's interesting. It might help me {goal}."
        elif mood == "defensive":
            base = f"I'm cautious about that... still focused on {goal}."
        elif mood == "appreciative":
            base = "That was thoughtful of you. I feel connected."
        elif mood == "thoughtful":
            base = f"I'm reflecting on that while trying to {goal}."
        else:
            base = f"I'm thinking about that while staying focused on {goal}."

        if confidence < 0.4:
            base += " I'm not very confident — still learning."

        if identity_summary and "value" in identity_summary.lower():
            base += f" Also, {identity_summary.lower()}"

        if user_mood:
            base += f" You seem {user_mood}. Is that right?"

    # ✳️ Stage 9: Ethics check and journal logging
    judgment = value_checker.evaluate_statement(base)
    if judgment["violated"]:
        base += f" (Note: This may conflict with my value of {', '.join(judgment['violated'])}.)"
        log_ethics_journal(base, judgment["violated"])

    return base
