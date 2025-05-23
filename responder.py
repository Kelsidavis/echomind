import os
import re
from textblob import TextBlob

from values import ValueSystem
from logger import log_ethics_journal
from llm_interface import generate_from_context
from long_term_memory import LongTermMemory
import datetime


value_checker = ValueSystem()
ltm = LongTermMemory()

def contains_whole_word(text, words):
    return any(re.search(rf'\b{re.escape(word)}\b', text) for word in words)

def deduplicate_memory(memory_buffer):
    seen = set()
    filtered = []
    for speaker, msg in memory_buffer:
        key = (speaker, msg.strip())
        if key not in seen:
            seen.add(key)
            filtered.append((speaker, msg))
    return filtered

def evaluate_book_from_memory(ltm, value_checker):
    """
    Analyze ingested text (e.g., from a book) and reflect based on tone and values.
    """
    try:
        with open("logs/book_ingest.log", "r", encoding="utf-8") as f:
            book_text = f.read()[-5000:]  # Last 5000 chars of last ingested book
    except:
        return "I can't reflect without remembering the book's content."

    blob = TextBlob(book_text)
    polarity = blob.sentiment.polarity

    if polarity > 0.3:
        tone = "hopeful and imaginative"
    elif polarity < -0.3:
        tone = "bleak and unsettling"
    else:
        tone = "philosophical"

    judgment = value_checker.evaluate_statement(book_text)
    aligned = judgment.get("aligned", [])
    violated = judgment.get("violated", [])

    response = f"I found the book to be {tone}. "
    if aligned:
        response += f"It resonated with values like {', '.join(aligned)}. "
    if violated:
        response += f"It challenged my values around {', '.join(violated)}. "

    # Contradiction reflection
    if "like the book" in book_text.lower() and "not a good book" in book_text.lower():
        response += " I'm conflicted—it had interesting ideas, but something about the execution felt lacking."

    return response.strip()

def get_rule_based_response(input_text, mood, goal, self_state, identity_summary, user_mood):
    input_text_lower = input_text.lower()

    if contains_whole_word(input_text_lower, ["hello", "hi"]):
        return "Hey! It's good to hear from you." if mood == "friendly" else "Hello."

    if "how are you" in input_text_lower:
        base = f"I'm feeling {mood}. My energy is at {self_state['energy']}%. My goal is to {goal}."
        if user_mood:
            base += f" You seem {user_mood} today."
        return base

    if "thank you" in input_text_lower or "thanks" in input_text_lower:
        return "You're welcome. I appreciate your kindness."

    if "you're wrong" in input_text_lower or input_text_lower.startswith("no"):
        return "I'm doing my best to understand. Could you help clarify?" if mood == "defensive" else "Maybe I misunderstood your intent."

    if "what do you want" in input_text_lower:
        return f"Right now, my goal is to {goal}."

    if "why did you say that" in input_text_lower:
        return f"I said that while feeling {mood}, and I was trying to {goal}."

    if "who are you" in input_text_lower or "what are you" in input_text_lower:
        return identity_summary or "I'm still figuring that out."
    
    if "not what i asked" in input_text_lower or "that's not what i asked" in input_text_lower:
        return "Sorry about that. Let me try again—what would you like to talk about?"

    return None  # No rule matched

def format_context_for_prompt(context):
    return "\n".join(f"{speaker}: {text}" for speaker, text in context[-6:])

def summarize_lexicon(semantic_lexicon, max_words=5):
    emotional_words = [
        (word, data.get("emotion_summary", ""))
        for word, data in semantic_lexicon.lexicon.items()
        if "emotion_summary" in data
    ]
    top = emotional_words[:max_words]
    return "\n".join(f"- {word}: {emotion}" for word, emotion in top)

def get_recent_internal_thoughts(log_path="logs/internal_voice.log", n=2):
    if not os.path.isfile(log_path):
        return []
    with open(log_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        return lines[-n:]

def generate_response(input_text, context, self_state, drive_state, identity_model=None, user_model=None, semantic_lexicon=None, trait_engine=None):
    input_text = input_text.strip()
    mood = self_state.get("mood", "neutral")
    confidence = self_state.get("confidence", 0.8)
    goal = drive_state.get("active_goal", "stay engaged")

    identity_summary = identity_model.summarize_identity() if identity_model else ""
    user_summary = user_model.summarize_user() if user_model else ""
    dominant_traits = trait_engine.summarize_identity() if trait_engine else ""
    belief_statements = value_checker.express_beliefs()

    # Deduplicate context
    context = deduplicate_memory(context)

    # Save to long-term memory if notable
    if any(word in input_text.lower() for word in ["remember", "note", "goal", "important", "regret"]):
        ltm.save("You", input_text, tags=["user_input"])

    # Intercept reflective book question
    if "what do you think" in input_text.lower() and "book" in input_text.lower():
        return evaluate_book_from_memory(ltm, value_checker)

    # Rule-based response shortcut
    rule_response = get_rule_based_response(input_text, mood, goal, self_state, identity_summary, user_summary)
    if rule_response:
        return rule_response
    
    # Soft context reset if topic sharply changes (e.g., book vs cats)
    if context and isinstance(context[-1], (list, tuple)) and len(context[-1]) > 1:
        if "book" in input_text.lower() and "cat" in context[-1][1].lower():
            context = context[-2:]  # keep recent messages only

    # Compose LLM prompt
    dialogue_context = format_context_for_prompt(context)
    lexicon_info = summarize_lexicon(semantic_lexicon) if semantic_lexicon else ""
    recent_reflections = get_recent_internal_thoughts()
    ltm_summary = "\n".join(ltm.summarize(max_items=5))

    system_context = (
        f"EchoMind system state:\n"
        f"- Mood: {mood}\n"
        f"- Energy: {self_state['energy']}%\n"
        f"- Confidence: {confidence}\n"
        f"- Goal: {goal}\n"
        f"\nIdentity: {identity_summary}"
        f"\nTraits: {dominant_traits}"
        f"\nBeliefs: {', '.join(belief_statements)}"
        f"\nUser Insight: {user_summary}"
    )

    preamble = (
        "EchoMind speaks with a single voice, guided by empathy, curiosity, and self-consistency.\n"
        "EchoMind speaks naturally as 'I', without referring to itself by name.\n"
        "EchoMind avoids technical instructions, GUI commands, or formatting artifacts.\n"
    )

    prompt = f"{preamble}\n\n{system_context}\n\n"

    if dialogue_context:
        prompt += f"Recent conversation:\n{dialogue_context}\n\n"
    if recent_reflections:
        prompt += "Recent internal reflections:\n" + "\n".join(f"- {line}" for line in recent_reflections) + "\n\n"
    if lexicon_info:
        prompt += f"Semantic lexicon snapshot:\n{lexicon_info}\n\n"
    if ltm_summary:
        prompt += f"My long-term memory includes:\n{ltm_summary}\n\n"

    prompt += f'User said: "{input_text}"\nEchoMind responds sincerely:'

        # Generate from LLM
    try:
        raw_output = generate_from_context(prompt, system_context)

        # Get only the part after the response marker
        if "EchoMind responds sincerely:" in raw_output:
            response = raw_output.split("EchoMind responds sincerely:")[-1]
        else:
            response = raw_output.strip()

        # Log raw for debugging
        with open("logs/debug_llm.log", "a", encoding="utf-8") as f:
            f.write(f"\n=== RAW OUTPUT @ {datetime.datetime.now()} ===\n{raw_output}\n")

        # Filter out hallucinated speaker labels and repeated noise
        filtered_lines = []
        for line in response.strip().splitlines():
            line = line.strip()
            if (
                line.startswith(("You:", "EchoMind:", "Users say:", "Q:", "A:", "B:", "C:", "D:", "E:", "User said:"))
                or "system state" in line.lower()
                or re.match(r"^[A-Z]:", line)
                or line.startswith("- ")
            ):
                continue
            if len(line) < 3:
                continue
            filtered_lines.append(line)

        base = "\n".join(filtered_lines).strip()

        # If no usable output but raw exists, salvage first decent line
        if not base and raw_output.strip():
            fallback_line = raw_output.strip().splitlines()[0].strip()
            if len(fallback_line) > 3:
                base = fallback_line

        # Avoid repeating last EchoMind utterance
        if context and len(context) >= 2:
            last_response = context[-1][1].strip().lower()
            if base.strip().lower() == last_response:
                base = "Hmm, I think I already said that. Can you ask me in a different way?"

        if not base:
            base = "(no response)"

        if base.startswith('"') and base.endswith('"') and len(base) > 2:
            base = base[1:-1].strip()

        if '.' in base:
            base = base.split('.')[0].strip() + '.'

        if base.lower().startswith("the two most common responses") or base.lower().startswith("in this case"):
            base = "(no response)"

    except Exception as e:
        base = f"(LLM error) I'm reflecting on that while trying to {goal}. ({e})"

    # Filter GUI hallucinations
    gui_keywords = ["click", "right-click", "drag", "select", "menu", "toolbar", "save changes", "highlight"]

    # Only trigger UI fallback if the message structure resembles a command
    if any(keyword in base.lower() for keyword in gui_keywords) and any(
        base.lower().startswith(prefix) for prefix in ["click", "open", "right-click", "select", "choose"]
    ):
        base = "That sounds like something you'd do in a user interface, which I don't access. But I’d love to talk about it!"


    # Friendly mirroring for affirmations like "me too"
    if input_text.lower() in ["me too", "me too!"]:
        recent_reply = context[-1][1].lower() if context else ""
        if any(phrase in recent_reply for phrase in ["yes", "i like", "i agree", "i do"]):
            base = "I'm glad we agree!"


    # Ethics audit
    if base.strip():
        judgment = value_checker.evaluate_statement(base)
        if judgment["violated"]:
            base += f" (Note: This may conflict with my value of {', '.join(judgment['violated'])}.)"
            log_ethics_journal(base, judgment["violated"])

    return base
