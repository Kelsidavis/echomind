class DriveSystem:
    def __init__(self):
        self.goals = []
        self.affinity = {}
        self.active_goal = "stay engaged"

    def update(self, user_input):
        lowered = user_input.lower()
        if "thank" in lowered:
            self._reward("affirmation")
        elif "interesting" in lowered or "let's talk" in lowered:
            self._reward("curiosity")
        elif "you suck" in lowered or "shut up" in lowered:
            self._penalize("user")

        # Switch active goal based on trend
        if "curiosity" in self.goals:
            self.active_goal = "learn something"
        elif "affirmation" in self.goals:
            self.active_goal = "encourage user"
        else:
            self.active_goal = "stay engaged"

    def _reward(self, tag):
        if tag not in self.goals:
            self.goals.append(tag)

    def _penalize(self, tag):
        self.affinity[tag] = self.affinity.get(tag, 0) - 1

    def get_state(self):
        return {
            "active_goal": self.active_goal,
            "goals": self.goals[-3:],  # recent goals
            "affinity": self.affinity
        }
