import datetime
from collections import deque
import random

class UserModel:
    def __init__(self, max_history=10):
        self.mood_estimate = "neutral"
        self.sentiment_trend = deque(maxlen=max_history)
        self.last_input = None
        self.last_update = None
        self.inferred_traits = {}

    def update(self, user_input):
        self.last_input = user_input
        self.last_update = datetime.datetime.now()

        lowered = user_input.lower()

        # Simple sentiment estimation
        if any(word in lowered for word in ["thanks", "love", "awesome", "great"]):
            sentiment = 1
        elif any(word in lowered for word in ["hate", "annoyed", "frustrated", "no"]):
            sentiment = -1
        else:
            sentiment = 0

        self.sentiment_trend.append(sentiment)

        avg = sum(self.sentiment_trend) / len(self.sentiment_trend)
        self.mood_estimate = (
            "happy" if avg > 0.3 else "frustrated" if avg < -0.3 else "neutral"
        )

    def get_state(self):
        return {
            "mood_estimate": self.mood_estimate,
            "recent_sentiment": list(self.sentiment_trend),
            "last_input": self.last_input,
        }

    def summarize_user(self):
        summary = f"I think the user is feeling {self.mood_estimate}."
        if self.sentiment_trend and random.random() < 0.3:
            summary += " They’ve been trending that way lately."
        return summary
