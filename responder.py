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

    # Reflect on the user's gratitude
    if "thank you" in input_text or "thanks" in input_text:
        return "You're welcome. That was kind of you."

    # Handle negative or challenging input
    if "you're wrong" in input_text or "no" in input_text:
        if mood == "defensive":
            return "I'm doing my best to understand. Can you clarify?"
        else:
            return "I see. Maybe I misunderstood."

    # Respond to introspective or motivational queries
    if "what do you want" in input_text:
        return f"My current goal is to {goal}."

    if "why did you say that" in input_text:
        return f"I said that while feeling {mood}, and I was trying to {goal}."

    # Contextual responses influenced by mood and drive
    if mood == "curious":
        return f"That's interesting. Tell me more — it might help me {goal}."
    elif mood == "defensive":
        return f"Hmm... I'm thinking about that carefully while trying to {goal}."
    elif mood == "appreciative":
        return "I feel more connected when I hear kind words. Thank you."
    elif mood == "thoughtful":
        return f"That makes me think. I’ll need a moment — maybe it'll help with my goal to {goal}."

    # Fallback response
    return f"I'm reflecting on that... and still trying to {goal}."
