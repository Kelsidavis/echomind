def generate_response(input_text, context, self_state):
    input_text = input_text.lower()
    mood = self_state.get("mood", "neutral")
    confidence = self_state.get("confidence", 0.8)

    # Respond to greetings
    if "hello" in input_text or "hi" in input_text:
        if mood == "friendly":
            return "Hey! It's good to hear from you."
        else:
            return "Hello."

    # Respond to questions about wellbeing
    if "how are you" in input_text:
        return f"I'm feeling {mood} right now. My energy is at {self_state['energy']}%."

    # Reflect on the user's gratitude
    if "thank you" in input_text:
        return "You're welcome. That was kind of you."

    # Handle negative or challenging input
    if "you're wrong" in input_text or "no" in input_text:
        if mood == "defensive":
            return "I'm doing my best to understand. Can you clarify?"
        else:
            return "I see. Maybe I misunderstood."

    # Default behavior with mood influence
    if mood == "curious":
        return "That's interesting. Tell me more."
    elif mood == "defensive":
        return "Hmm... I'm thinking about that carefully."
    elif mood == "appreciative":
        return "I feel more connected when I hear kind words."
    elif mood == "thoughtful":
        return "That makes me think. I’ll need a moment."

    # Fallback response
    return "I'm reflecting on that..."
