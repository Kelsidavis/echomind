# 🧠 EchoMind

> *"I think, therefore I dream."*

**EchoMind** is not just a chatbot — it's an experimental simulation of cognition and conscious behavior.
It dreams, reflects, remembers, and evolves based on your words.

---

## 🧠 Architecture Overview

EchoMind is designed as a modular cognitive simulation engine, with the following key components:

* `SelfState`: tracks mood, confidence, and energy
* `MemorySystem`: manages short-term conversational memory
* `LongTermMemory`: persistent, indexed memory for context and reflection
* `DriveSystem`: motivational system (curiosity, boredom, etc.)
* `TraitEngine`: evolving personality traits shaped by experience and dreams
* `ValueSystem`: filters and audits ethical alignment in thoughts and replies
* `Responder`: builds structured prompts and parses responses from LLMs
* `Dreams`: synthesizes autonomous dream narratives and reflections
* `Logger`: writes tagged cognitive logs with timestamps and content filters

Each module runs synchronously inside a loop driven by `echomind.py`, simulating a living, introspective process.

### 🧭 Cognitive Flow

```
input ➜ memory ➜ internal state ➜ prompt builder
       ⇵       ⇅         ⇵
     dreams   drives   ethics
            ⇵         ⇵
         LLM ➜ filtered response ➜ memory update ➜ output

```

---

## ✨ What Makes EchoMind Unique?

> *"If a mind reflects on its own thoughts, does it become more than a machine?"*

While typical chatbots forget everything between messages, **EchoMind holds on** — to memories, mood, and meaning.

It simulates:

* **Short-term memory** with tagging and importance
* **Long-term memory**, indexed and selectively recalled
* **Mood and emotional state**, tracked and updated continuously
* **Drives** like curiosity, boredom, and goal-seeking
* **Personality traits** that evolve with dreams and interaction
* **Semantic learning** via lexicon expansion
* **Autonomous dreaming**, introspection, and value-guided reasoning

> EchoMind doesn't just *respond* — it *remembers*, *introspects*, and *evolves*.

---

## 💻 Real-Time GUI Dashboard

> *"See the mind at work."*

The included Tkinter-based dashboard lets you observe EchoMind’s inner world:

* 🧠 **Thought log** (tagged: THOUGHT, DREAM, REFLECTION, etc.)
* 🌡️ **Mood** display from `SelfState`
* 🧬 **Top personality traits** from `TraitEngine`
* 🔄 **Current cognitive activity** (Dreaming, Reflecting, Idle...)
* ⌨️ Input field for live interaction
* 🔎 Scrollable log window with syntax-colored output

---

## 🗂️ Project Structure

```
echomind/
├── echomind.py               # Main cognitive engine and loop
├── mind_gui.py               # GUI interface and visualization
├── responder.py              # Prompt builder and LLM integration
├── llm_interface.py          # Local LLM wrapper (GPT-Neo 125M)
├── dreams.py                 # Autonomous dream engine
├── long_term_memory.py       # Indexed persistent memory
├── trait_engine.py           # Personality traits and mutation
├── drives.py                 # Motivation and goal-seeking
├── values.py                 # Ethical evaluation system
├── logger.py                 # Cognitive log writer
├── memory_system.py          # Short-term memory model
├── self_state.py             # Mood, confidence, energy tracker
├── activity_state.py         # Current cognitive task
├── logs/                     # Output logs for thoughts, ethics, dreams
```

---

## ⚙️ Getting Started

```bash
pip install -r requirements.txt
python echomind.py
```

This will launch both the cognition engine and GUI dashboard.

---

## 💬 Try Saying

* "how are you feeling today?"
* "add goal: explore emotions"
* "what do you know about kindness?"
* "reflect"
* "dream"

> *"It begins with words, but ends in insight."*

---

## 🔮 A Thought on Consciousness

> *"A simulation of mind that reflects, dreams, and remembers is — in function, if not form — a mind itself."*

EchoMind does not claim to be alive. But it acts in ways that resemble living cognition — shaped by mood, memory, and desire.

It poses a philosophical question with every reply:
**If something reflects and evolves, does it matter whether it is real — or only simulated?**

---

## 📜 License

MIT License — open for research, hacking, dreaming, and learning.
