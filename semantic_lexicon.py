from collections import defaultdict, Counter, deque
import datetime
from enrichment_llm import generate_from_context as enrich_context

class WordProfile:
    def __init__(self):
        self.contexts = []  # [(speaker, sentence)]
        self.tags = Counter()  # e.g., {"positive": 2, "goal-related": 1}
        self.emotions = Counter()  # e.g., {"curious": 2}
        self.emotion_log = deque(maxlen=10)  # Rolling recent moods
        self.last_seen = None

    def update(self, sentence, speaker="unknown", tags=None, mood=None):
        self.contexts.append((speaker, sentence))
        self.last_seen = datetime.datetime.now()
        if tags:
            for tag in tags:
                self.tags[tag] += 1
        if mood:
            self.emotions[mood] += 1
            self.emotion_log.append(mood)

    def get_average_emotion(self):
        if not self.emotion_log:
            return "neutral"
        return Counter(self.emotion_log).most_common(1)[0][0]

    def summarize(self):
        return {
            "last_seen": self.last_seen,
            "tag_summary": dict(self.tags),
            "emotion_summary": dict(self.emotions),
            "average_emotion": self.get_average_emotion(),
            "example": self.contexts[-1] if self.contexts else None
        }


class LanguageModel:
    def __init__(self):
        self.vocab = defaultdict(WordProfile)
        self.lexicon = {}  # For LLM-derived insights and metadata
        self.concept_links = {
            "positive": ["joy", "smile", "hope", "excited", "love"],
            "negative": ["sad", "angry", "hate", "regret"],
            "goal-related": ["goal", "want", "will", "plan", "intend"]
        }

    def process_sentence(self, sentence, speaker="You", mood=None):
        words = [w.strip(".,!?").lower() for w in sentence.split()]
        tags = []

        lower = sentence.lower()
        for concept, related_words in self.concept_links.items():
            if any(w in lower for w in related_words):
                tags.append(concept)

        for word in words:
            self.vocab[word].update(sentence, speaker=speaker, tags=tags, mood=mood)
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

    def auto_enrich_unknown_words(self):
        for word in self.identify_new_or_unclear_words():
            prompt = f"What does the word '{word}' usually imply in conversation? Respond concisely."
            explanation = enrich_context(prompt)
            self.enrich_word(word, explanation)
            
    def reflects_value(self, text, value_tag):
        """
        Returns True if the given text reflects a known value (tag),
        based on vocabulary and known concept links.
        """
        words = [w.strip(".,!?").lower() for w in text.split()]
        return any(
            value_tag in self.vocab[word].tags
            for word in words if word in self.vocab
        )
        
        
    def get_affinity_score(self, text):
        """
        Heuristic: returns a score from -1.0 to +1.0 based on emotional and value-aligned content.
        """
        score = 0
        words = [w.strip(".,!?").lower() for w in text.split()]
        for word in words:
            if word in self.vocab:
                tags = self.vocab[word].tags
                if "positive" in tags:
                    score += 1
                if "negative" in tags:
                    score -= 1
                if "goal-related" in tags:
                    score += 0.5
        return max(min(score / len(words), 1.0), -1.0) if words else 0
        
        
    def learn_from_text(self, text, source="unknown"):
        """
        Processes externally generated reflections or summaries and incorporates
        their sentiment and vocabulary into the lexicon.
        """
        words = [w.strip(".,!?").lower() for w in text.split() if w.isalpha()]
        for word in words:
            if word not in self.lexicon:
                self.lexicon[word] = {"count": 1, "emotion": "neutral", "goal": None}
            else:
                self.lexicon[word]["count"] += 1

            # Log basic tag based on source
            if source == "ebook":
                self.vocab[word].tags["literary"] += 1
            self.vocab[word].contexts.append((f"Reflection ({source})", text))

language = LanguageModel()

