from collections import Counter

class TraitEngine:
    def __init__(self):
        self.trait_log = []
        self.trait_counts = Counter()

    def analyze_memories(self, memory_buffer):
        """
        Extract dominant behavioral patterns from memory and derive traits.
        """
        if not memory_buffer:
            return None

        traits = []

        for speaker, message in memory_buffer:
            msg = message.lower()

            if "i care" in msg or "that matters" in msg:
                traits.append("empathetic")
            if "i'm trying" in msg or "i want to grow" in msg:
                traits.append("growth-oriented")
            if "i don't lie" in msg or "i tell the truth" in msg:
                traits.append("honest")
            if "i always" in msg or "i never" in msg:
                traits.append("principled")
            if "used to" in msg or "i’ve changed" in msg:
                traits.append("evolving")

        self.trait_counts.update(traits)
        if traits:
            self.trait_log.append(traits)

        return traits

    def get_dominant_traits(self, n=3):
        return self.trait_counts.most_common(n)

    def summarize_identity(self):
        top_traits = self.get_dominant_traits()
        return "I believe I am: " + ", ".join(trait for trait, _ in top_traits)
