from collections import defaultdict, Counter
import datetime

class WordProfile:
    def __init__(self):
        self.contexts = []  # [(speaker, sentence)]
        self.tags = Counter()  # e.g., {"positive": 2, "goal-related": 1}
        self.emotions = Counter()  # e.g., {"curious": 2}
        self.last_seen = None

    def update(self, sentence, speaker="unknown", tags=None, mood=None):
        self.contexts.append((speaker, sentence))
        self.last_seen = datetime.datetime.now()
        if tags:
            for tag in tags:
                self.tags[tag] += 1
        if mood:
            self.emotions[mood] += 1

    def summarize(self):
        return {
            "last_seen": self.last_seen,
            "tag_summary": dict(self.tags),
            "emotion_summary": dict(self.emotions),
            "example": self.contexts[-1] if self.contexts else None
        }


class LanguageModel:
    def __init__(self):
        self.vocab = defaultdict(WordProfile)
        self.lexicon = {}  # For LLM-derived insights

    def process_sentence(self, sentence, speaker="You", mood=None):
        words = [w.strip(".,!?").lower() for w in sentence.split()]
        tags = []

        # Tagging heuristics
        lower = sentence.lower()
        if any(word in lower for word in ["love", "hope", "joy", "smile", "excited"]):
            tags.append("positive")
        if any(word in lower for word in ["sad", "angry", "hate", "regret"]):
            tags.append("negative")
        if "goal" in lower or "i want" in lower or "i will" in lower:
            tags.append("goal-related")

        for word in words:
            self.vocab[word].update(sentence, speaker=speaker, tags=tags, mood=mood)
            # Count usage for lexicon if not already
            if word not in self.lexicon:
                self.lexicon[word] = {"count": 1, "emotion": "neutral", "goal": None}
            else:
                self.lexicon[word]["count"] += 1

    def get_word_summary(self, word):
        word = word.lower()
        if word in self.vocab:
            summary = self.vocab[word].summarize()
            if word in self.lexicon and "llm_context" in self.lexicon[word]:
                summary["llm_context"] = self.lexicon[word]["llm_context"]
            return summary
        return {"error": "Word not seen yet"}

    def get_known_words(self):
        return list(self.vocab.keys())

    def get_most_tagged_words(self, tag, top_n=5):
        return sorted(
            [(w, p.tags[tag]) for w, p in self.vocab.items() if tag in p.tags],
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

    def get_concepts_by_tag(self, tag, min_score=2):
        return [
            word for word, profile in self.vocab.items()
            if profile.tags[tag] >= min_score
        ]

    def get_frequent_user_values(self, speaker="You"):
        meaning = Counter()
        for word, profile in self.vocab.items():
            for tag, count in profile.tags.items():
                if tag != "negative":
                    meaning[tag] += count
        return meaning.most_common(3)

    def identify_new_or_unclear_words(self, min_usage=2):
        return [
            word for word, info in self.lexicon.items()
            if info["count"] <= min_usage or info.get("emotion") == "neutral"
        ]

    def enrich_word(self, word, explanation):
        if word not in self.lexicon:
            self.lexicon[word] = {"count": 1, "emotion": "neutral", "goal": None}
        self.lexicon[word]["llm_context"] = explanation
