import random

class SelfState:
    def __init__(self):
        self.mood = "neutral"
        self.energy = 100
        self.confidence = 0.8

    def update(self, user_input):
        lowered = user_input.lower()
        if "thank you" in lowered:
            self.mood = "appreciative"
            self.confidence += 0.05
        elif "you're wrong" in lowered or "no" in lowered:
            self.mood = "defensive"
            self.confidence -= 0.1
        elif "hi" in lowered or "hello" in lowered:
            self.mood = "friendly"
        else:
            self.mood = random.choice(["neutral", "curious", "thoughtful"])

        # Decay and recovery dynamics
        self.energy = max(0, self.energy - 1)
        self.confidence = min(1.0, max(0.0, self.confidence))

    def get_state(self):
        return {
            "mood": self.mood,
            "energy": self.energy,
            "confidence": round(self.confidence, 2)
        }
        
    def update_mood_from_context(self, user_input, memory_context):
        # Naive example: mood shifts based on keywords
        if "thank" in user_input.lower():
            self.mood = "appreciated"
        elif "why" in user_input.lower():
            self.mood = "curious"
        elif "sorry" in user_input.lower():
            self.mood = "sympathetic"
        else:
            self.mood = "neutral"
    
        self.confidence = max(0.0, min(1.0, self.confidence + 0.05 if "I see" in user_input else -0.02))

