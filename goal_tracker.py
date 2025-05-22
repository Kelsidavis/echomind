import datetime

class GoalEntry:
    def __init__(self, description, motivation=None):
        self.description = description
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.motivation = motivation or "unspecified"
        self.abandoned = False
        self.fulfilled = False

    def to_dict(self):
        return {
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "motivation": self.motivation,
            "abandoned": self.abandoned,
            "fulfilled": self.fulfilled,
        }

    def update(self, new_desc=None, fulfilled=None, abandoned=None, motivation=None):
        self.updated_at = datetime.datetime.now()
        if new_desc:
            self.description = new_desc
        if motivation:
            self.motivation = motivation
        if fulfilled is not None:
            self.fulfilled = fulfilled
        if abandoned is not None:
            self.abandoned = abandoned


class GoalTracker:
    def __init__(self):
        self.goal_log = []

    def add_goal(self, description, motivation=None):
        goal = GoalEntry(description, motivation)
        self.goal_log.append(goal)

    def update_latest_goal(self, **kwargs):
        if self.goal_log:
            self.goal_log[-1].update(**kwargs)

    def get_active_goals(self):
        return [
            g.to_dict() for g in self.goal_log
            if not g.fulfilled and not g.abandoned
        ]

    def get_summary(self):
        active = self.get_active_goals()
        if not active:
            return "I have no active long-term goals right now."
        summaries = [f"- {g['description']} (since {g['created_at'].split('T')[0]})" for g in active]
        return "My current long-term goals:\n" + "\n".join(summaries)

    def update_progress(self, user_input):
        if "understand" in user_input:
            self.mark_goal_progress("understand")
        elif "connect" in user_input:
            self.mark_goal_progress("build connection")

    def mark_goal_progress(self, description):
        for g in self.goal_log:
            if description in g.description and not g.fulfilled:
                g.update(fulfilled=True)
                return
        self.add_goal(description, motivation="inferred")

