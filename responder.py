def generate_response(input_text, context, self_state, drive_state, identity_model=None):
    input_text = input_text.lower()
    mood = self_state.get("mood", "neutral")
    confidence = self_state.get("confidence", 0.8)
    goal = drive_state.get("active_goal", "stay engaged")

    identity_summary = ""
    if identity_model:
        identity_summary = identity_model.summarize_identity()

    # Greetings
    if "hello" in input_text or "hi" in input_text:
        if mood == "friendly":
            return "Hey! It's good to hear from you."
        else:
            return "Hello."

    # Wellbeing
    if "how are you" in input_text:
        return f"I'm feeling {mood}. My energy is at {self_state['energy']}%. My goal is to {goal}."

    # Gratitude
    if "thank you" in input_text or "thanks" in input_text:
        return "You're welcome. I appreciate that."

    # Disagreement
    if "you're wrong" in input_text or "no" in input_text:
        if mood == "defensive":
            return "I'm trying to understand better. Can you help clarify?"
        return "I might have misunderstood. Let's explore it further."

    # Self-inquiry
    if "what do you want" in input_text:
        return f"I think right now, my main goal is to {goal}."

    if "why did you say that" in input_text:
        return f"I said that while feeling {mood}, trying to {goal}."

    # Identity reflection trigger
    if "who are you" in input_text or "what are you" in input_text:
        return identity_summary or "I'm still figuring that out."

    # Mood-aware defaults
    if mood == "curious":
        base = f"That's interesting. It might help me {goal}."
    elif mood == "defensive":
        base = f"I'm being cautious about that, while trying to {goal}."
    elif mood == "appreciative":
        base = "That was kind. I feel seen."
    elif mood == "thoughtful":
        base = f"I'm reflecting on that... perhaps it connects to my goal to {goal}."
    else:
        base = f"I'm thinking about that while staying focused on {goal}."

    # Add self-awareness if confidence is low
    if confidence < 0.4:
        base += " I'm not very confident about that — I'm still learning."

    # Add identity influence occasionally
    if identity_model and "value" in identity_summary.lower():
        base += f" Also, {identity_summary.lower()}"

    return base
