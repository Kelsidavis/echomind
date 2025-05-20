import datetime

class SelfModel:
    def __init__(self):
        self.mood_history = []
        self.goal_history = []
        self.formative_events = []  # (timestamp, summary)
        self.identity_assertions = []  # user-facing declarations like "I value curiosity"

    def update(self, mood, goal, memory_context):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.mood_history.append((timestamp, mood))
        self.goal_history.append((timestamp, goal))

        # Look for important tags in memory and log if meaningful
        for speaker, message in memory_context[-3:]:
            if isinstance(message, str) and "[turning point]" in message.lower():
                self.formative_events.append((timestamp, message.strip()))

    def summarize_identity(self):
        if not self.mood_history:
            return "I haven't experienced enough to describe myself yet."

        moods = [m for _, m in self.mood_history[-10:]]
        mood_counts = {m: moods.count(m) for m in set(moods)}
        dominant_mood = max(mood_counts, key=mood_counts.get)

        goals = [g for _, g in self.goal_history[-10:]]
        goal_counts = {g: goals.count(g) for g in set(goals)}
        dominant_goal = max(goal_counts, key=goal_counts.get)

        summary = (
            f"I often feel {dominant_mood}, and my most consistent goal lately has been to {dominant_goal}."
        )

        if self.formative_events:
            summary += f" One moment that changed me was: \"{self.formative_events[-1][1]}\""

        return summary

    def export_model(self, path="logs/self_model.log"):
        try:
            with open(path, "a", encoding="utf-8") as file:
                file.write(f"\n[Self-Model Update @ {datetime.datetime.now()}]\n")
                file.write(self.summarize_identity() + "\n")
        except Exception as e:
            print(f"Failed to export self model: {e}")
