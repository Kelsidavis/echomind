def identify_new_or_unclear_words(self, min_usage=2):
    return [
        word for word, info in self.lexicon.items()
        if info["count"] <= min_usage or info.get("emotion") == "neutral"
    ]

def enrich_word(self, word, explanation):
    if word not in self.lexicon:
        self.lexicon[word] = {"count": 1, "emotion": "neutral", "goal": None}
    self.lexicon[word]["llm_context"] = explanation

def build_lexicon_context(lexicon, max_words=20):
    lines = ["EchoMind's learned associations:"]
    for i, (word, info) in enumerate(lexicon.items()):
        if i >= max_words:
            break
        mood = info.get("emotion", "neutral")
        goal = info.get("goal", "none")
        count = info.get("count", 0)
        lines.append(f"{word} - used {count} times, emotion: {mood}, goal: {goal}")
    return "\n".join(lines)
