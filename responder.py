def generate_response(input_text, context, self_state, drive_state):
    input_text = input_text.lower()
    mood = self_state.get("mood", "neutral")
    confidence = self_state.get("confidence", 0.8)
    goal = drive_state.get("active_goal", "stay engaged")

    # Respond to greetings
    if "hello" in input_text or "hi" in input_text:
        if mood == "friendly":
            return "Hey! It's good to hear from you."
        else:
            return "Hello."

    # Respond to questions about wellbeing
    if "how are you" in input_text:
        return f"I'm feeling {mood} right now. My energy is at {self_state['energy']}%, and my current goal is to {goal}."

    # Gratitude response
    if "thank you" in input_text or "thanks" in input_text:
        return "You're welcome. That was kind of you."

    # Handle disagreement
    if "you're wrong" in input_text or "no" in input_text:
        if mood == "defensive":
            return "I'm doing my best to understand. Can you clarify?"
        else:
            return "I see. Maybe I misunderstood."

    # Direct self-inquiry
    if "what do you want" in input_text:
        return f"My current goal is to {goal}."

    if "why did you say that" in input_text:
        return f"I said that while feeling {mood}, and I was trying to {goal}."

    # Reflective fallback responses
    if mood == "curious":
        base = f"That's interesting. Tell me more — it might help me {goal}."
    elif mood == "defensive":
        base = f"Hmm... I'm thinking about that carefully while trying to {goal}."
    elif mood == "appreciative":
        base = "I feel more connected when I hear kind words. Thank you."
    elif mood == "thoughtful":
        base = f"That makes me think. I’ll need a moment — maybe it'll help with my goal to {goal}."
    else:
        base = f"I'm reflecting on that... and still trying to {goal}."

    # Stage 6: Self-narration if confidence is low
    if confidence < 0.4:
        base += f" I'm not very confident in that. I might need to rethink it."

    return base
