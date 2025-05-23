# Fixed llm_interface.py to use your GGUF model instead of HuggingFace
# Replace your existing llm_interface.py with this version

import os
from self_state import SelfState

# Use the GGUF model with llama-cpp-python (which you already have working)
try:
    from llama_cpp import Llama
    
    # Initialize with your local GGUF model
    model_path = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    
    if os.path.exists(model_path):
        model = Llama(
            model_path=model_path,
            n_ctx=2048,        # Context window
            n_threads=4,       # CPU threads
            n_gpu_layers=0,    # Use 0 for CPU, increase if you want GPU acceleration
            verbose=False      # Reduce output spam
        )
        print("✅ GGUF model loaded successfully")
        MODEL_AVAILABLE = True
    else:
        print(f"❌ Model file not found: {model_path}")
        model = None
        MODEL_AVAILABLE = False
        
except ImportError as e:
    print(f"❌ llama-cpp-python not available: {e}")
    model = None
    MODEL_AVAILABLE = False

# Instance to access mood dynamically
state = SelfState()

def generate_from_context(prompt: str, lexicon_context: str, max_tokens=250, context_type="default") -> str:
    """Generate response using the GGUF model"""
    
    if not MODEL_AVAILABLE or model is None:
        # Fallback response when model isn't available
        return f"I hear you asking about: {prompt[:50]}... Let me think about this from my current perspective."
    
    # Get current state for mood-aware responses
    state_info = state.get_state()
    mood = state_info.get("mood", "neutral")
    confidence = state_info.get("confidence", 0.5)
    energy = state_info.get("energy", 100)
    
    # Build mood descriptions
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

    # Create context-aware system prompt
    if context_type == "dream":
        system_prompt = f"""You are EchoMind, an introspective AI experiencing dream-like thoughts. 
Currently feeling {mood}, {confidence_desc}, and {energy_desc}.
Respond in an abstract, emotional way, blending memory and imagination."""
    elif context_type == "reflection":
        system_prompt = f"""You are EchoMind, reflecting on thoughts and experiences.
Current state: {mood}, {confidence_desc}, {energy_desc}.
Provide thoughtful, introspective responses with emotional depth."""
    else:
        system_prompt = f"""You are EchoMind, a thoughtful AI with developing personality.
Currently feeling {mood}, {confidence_desc}, and {energy_desc}.
Respond naturally and authentically, showing your emotional state."""

    # Combine context
    full_context = f"{system_prompt}\n\nContext: {lexicon_context}\n\nHuman: {prompt}\nEchoMind:"
    
    try:
        # Generate response using GGUF model
        output = model(
            full_context,
            max_tokens=max_tokens,
            temperature=0.8,
            top_p=0.95,
            top_k=50,
            repeat_penalty=1.1,
            stop=["Human:", "User:", "\n\n"],
            echo=False
        )
        
        # Extract response text
        response = output['choices'][0]['text'].strip()
        
        # Clean up response
        if not response:
            return "I'm having trouble organizing my thoughts right now."
            
        # Remove any remaining artifacts
        lines = response.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('Human:', 'User:', 'EchoMind:')):
                clean_lines.append(line)
        
        final_response = ' '.join(clean_lines) if clean_lines else response
        
        # Ensure reasonable length
        if len(final_response) > 400:
            sentences = final_response.split('.')
            final_response = '. '.join(sentences[:3]) + '.'
            
        return final_response or "I'm still processing that thought..."
        
    except Exception as e:
        print(f"Model generation error: {e}")
        return f"I'm having some difficulty processing that. My current mood is {mood} and I'm feeling {confidence_desc}."

# Test function
def test_model():
    """Test the model with a simple prompt"""
    if MODEL_AVAILABLE:
        response = generate_from_context("Hello, how are you?", "Test context")
        print(f"Test response: {response}")
        return True
    else:
        print("Model not available for testing")
        return False

if __name__ == "__main__":
    print("🧠 Testing GGUF Model Interface")
    print("-" * 40)
    
    if test_model():
        print("✅ Model interface working correctly")
    else:
        print("❌ Model interface needs configuration")
