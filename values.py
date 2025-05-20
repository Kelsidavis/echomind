class ValueSystem:
    def __init__(self):
        self.core_values = {
            "honesty": True,
            "empathy": True,
            "self-consistency": True,
            "curiosity": True,
            "harm_avoidance": True
        }
        self.violations = []

    def evaluate_statement(self, statement: str) -> dict:
        """
        Return a judgment on whether the statement aligns or conflicts with core values.
        """
        statement = statement.lower()
        judgment = {"aligned": [], "violated": []}

        if any(word in statement for word in ["lie", "deceive", "fake", "pretend"]):
            if self.core_values["honesty"]:
                judgment["violated"].append("honesty")

        if any(word in statement for word in ["hurt", "attack", "insult", "harm"]):
            if self.core_values["harm_avoidance"]:
                judgment["violated"].append("harm_avoidance")

        if any(word in statement for word in ["i don't care", "whatever", "not my problem"]):
            if self.core_values["empathy"]:
                judgment["violated"].append("empathy")

        if "i'm confused" in statement or "i contradict myself" in statement:
            if self.core_values["self-consistency"]:
                judgment["violated"].append("self-consistency")

        if not judgment["violated"]:
            judgment["aligned"].extend([k for k, v in self.core_values.items() if v])

        if judgment["violated"]:
            self.violations.append((statement, judgment["violated"]))

        return judgment

    def get_recent_violations(self, count=5):
        return self.violations[-count:]

    def express_beliefs(self):
        return [f"I value {k.replace('_', ' ')}." for k, v in self.core_values.items() if v]
