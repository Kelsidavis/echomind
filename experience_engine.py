from collections import Counter
import datetime

class ExperienceEngine:
    def __init__(self):
        self.feedback_log = []
        self.outcome_counts = Counter()
        self.behavior_modifiers = {}

    def record_experience(self, context, response, outcome):
        """
        Log experience and outcome type: success, failure, joy, friction, etc.
        """
        self.feedback_log.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "context": context[-3:],  # last 3 exchanges
            "response": response,
            "outcome": outcome
        })
        self.outcome_counts[outcome] += 1

    def adjust_trait_weight(self, trait_engine):
        """
        Apply simple feedback trends to personality traits.
        """
        if self.outcome_counts["failure"] > self.outcome_counts["success"]:
            trait_engine.trait_counts["cautious"] += 1
        elif self.outcome_counts["success"] > self.outcome_counts["failure"]:
            trait_engine.trait_counts["resilient"] += 1

    def get_summary(self):
        return dict(self.outcome_counts)
