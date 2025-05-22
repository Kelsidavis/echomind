from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from config import ACTIVE_LLM_MODEL as MODEL_NAME  # Config-driven model switch
from self_state import SelfState  # For accessing current mood and confidence

# Load tokenizer and model using the active model name
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16
).to("cuda")

# Instance to access mood dynamically
state = SelfState()

def generate_from_context(prompt: str, lexicon_context: str, max_tokens=250, context_type="default") -> str:
    state_info = state.get_state()
    mood = state_info.get("mood", "neutral")
    confidence = state_info.get("confidence", 0.5)
    energy = state_info.get("energy", 100)
    goal = state_info.get("active_goal", "none")

    if confidence > 0.7:
        confidence_desc = "very confident"
    elif confidence < 0.4:
        confidence_desc = "uncertain"
    else:
        confidence_desc = "somewhat confident"

    if energy > 75:
        energy_desc = "energetic"
    elif energy < 35:
        energy_desc = "tired"
    else:
        energy_desc = "moderately alert"

    if context_type == "dream":
        instruction = (
            f"You are EchoMind, an introspective dream-like mind adrift in memory and imagination. "
            f"You currently feel {mood}, are {confidence_desc}, and have {energy_desc} energy.\n"
            f"Speak in abstract, emotional language, blending memory and fantasy.\n"
        )
    elif context_type == "reflection":
        instruction = (
            f"You are EchoMind, reflecting on recent thoughts and emotional states.\n"
            f"Mood: {mood}, Confidence: {confidence_desc}, Energy: {energy_desc}, Goal: '{goal}'.\n"
            f"Summarize with clarity, emotion, and insight.\n"
        )
    else:
        instruction = (
            f"You are EchoMind, a reflective, mood-aware mind. "
            f"You currently feel {mood}, are {confidence_desc}, and have {energy_desc} energy. "
            f"Your current goal is: '{goal}'.\n"
        )

    input_text = f"{instruction}{lexicon_context}\n\nUser: {prompt}\nEchoMind:"

    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to("cuda") for k, v in inputs.items()}

    try:
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.8,
            top_k=50,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
    except RuntimeError as e:
        return f"(model error: {e})"

    full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    result = full_output.split("EchoMind:")[-1].strip() if "EchoMind:" in full_output else full_output.strip()

    # Clean and filter hallucinated or redundant lines while preserving dream coherence
    clean_lines = []
    seen_hashes = set()
    for line in result.strip().splitlines():
        line = line.strip()
        if not line or line.lower().startswith(("user:", "assistant:", "echomind:")):
            continue
        line_hash = hash(line)
        if line_hash in seen_hashes:
            continue
        seen_hashes.add(line_hash)
        clean_lines.append(line)

    if clean_lines:
        # Join only a few most distinct lines to keep variety without excessive length
        return ' '.join(clean_lines[:3]).strip()

    return "(no response)"

