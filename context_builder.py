# echomind/context_builder.py
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
