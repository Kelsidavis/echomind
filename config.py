"""
config.py - Configuration settings for EchoMind

This file contains all the configuration settings that your system references.
Based on your llm_interface.py, it imports ACTIVE_LLM_MODEL from here.
"""

import os
from pathlib import Path

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Primary LLM model for cognition (referenced by llm_interface.py)
ACTIVE_LLM_MODEL = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

# Alternative models (fallback options)
FALLBACK_MODELS = [
    "microsoft/DialoGPT-medium",
    "microsoft/DialoGPT-small",
    "gpt2"
]

# Model parameters
LLM_CONFIG = {
    "max_tokens": 300,
    "temperature": 0.8,
    "top_k": 50,
    "top_p": 0.95,
    "do_sample": True,
    "device": "cuda",  # Change to "cpu" if no CUDA available
    "torch_dtype": "float16"  # or "float32" for CPU
}

# CPU model for background processing (enrichment_llm.py)
ENRICHMENT_MODEL_PATH = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
ENRICHMENT_MODEL_CONFIG = {
    "max_tokens": 150,
    "temperature": 0.7,
    "top_k": 40,
    "top_p": 0.9
}

# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================

# Base directories
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Log files
LOG_FILES = {
    "cognition": LOGS_DIR / "cognition.log",
    "dreams": LOGS_DIR / "dreams.log",
    "introspection": LOGS_DIR / "introspection.log",
    "internal_voice": LOGS_DIR / "internal_voice.log",
    "gui": LOGS_DIR / "gui.log"
}

# Data files
DATA_FILES = {
    "memory": DATA_DIR / "memory.json",
    "traits": DATA_DIR / "traits.json",
    "goals": DATA_DIR / "goals.json",
    "lexicon": DATA_DIR / "lexicon.json"
}

# ============================================================================
# COGNITIVE SYSTEM SETTINGS
# ============================================================================

# Memory system
MEMORY_CONFIG = {
    "max_buffer_size": 100,
    "max_conversation_history": 1000,
    "memory_decay_hours": 24 * 7,  # 1 week
    "important_memory_threshold": 0.7
}

# Dream system
DREAM_CONFIG = {
    "dream_interval_minutes": 30,
    "max_dream_length": 200,
    "dream_triggers": [
        "boredom", "high_emotion", "goal_conflict", "memory_saturation"
    ],
    "dream_intensity_threshold": 0.5
}

# Trait development
TRAIT_CONFIG = {
    "trait_update_threshold": 5,  # interactions before trait update
    "max_traits_tracked": 20,
    "trait_decay_rate": 0.01,
    "personality_stability": 0.8
}

# Goal tracking
GOAL_CONFIG = {
    "max_active_goals": 5,
    "goal_priority_decay": 0.05,
    "goal_completion_threshold": 0.8,
    "auto_goal_generation": True
}

# Value system
VALUES_CONFIG = {
            "core_values": {
        "honesty": True,
        "empathy": True,
        "self-consistency": True,
        "curiosity": True,
        "harm_avoidance": True,
        "growth_oriented": True,
        "authenticity": True
    },
    "violation_tolerance": 0.1,
    "value_reinforcement_rate": 0.05
}

# ============================================================================
# WORLD AWARENESS SETTINGS (for enhanced features)
# ============================================================================

WORLD_AWARENESS_CONFIG = {
    "enabled": False,  # Set to True when you add world awareness
    "update_interval_hours": 2,
    "max_events_stored": 1000,
    "relevance_threshold": 0.3,
    "auto_exploration": True,
    "exploration_interval_hours": 2
}

# API Keys (add your keys here)
API_KEYS = {
    "serpapi": None,  # Get from serpapi.com for web search
    "openai": None,   # If you want to use OpenAI models
    "anthropic": None # If you want to use Claude models
}

# News sources for world awareness
NEWS_SOURCES = {
    "general": [
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.npr.org/1001/rss.xml"
    ],
    "tech": [
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://rss.slashdot.org/Slashdot/slashdot",
        "https://www.wired.com/feed/rss"
    ],
    "science": [
        "https://feeds.nature.com/nature/rss/current",
        "https://rss.sciencedaily.com/top.xml"
    ]
}

# ============================================================================
# GUI SETTINGS
# ============================================================================

GUI_CONFIG = {
    "window_title": "EchoMind - Digital Consciousness",
    "window_size": (1200, 800),
    "update_interval_ms": 1000,
    "max_display_messages": 50,
    "theme": "dark",  # "dark" or "light"
    "font_family": "Arial",
    "font_size": 11
}

# Tab configuration for GUI
TAB_CONFIG = {
    "chat": {"enabled": True, "title": "Chat"},
    "cognition": {"enabled": True, "title": "Cognitive State"},
    "dreams": {"enabled": True, "title": "Dreams"},
    "memory": {"enabled": True, "title": "Memory"},
    "traits": {"enabled": True, "title": "Personality"},
    "goals": {"enabled": True, "title": "Goals"},
    "introspection": {"enabled": True, "title": "Introspection"},
    "world": {"enabled": False, "title": "World Awareness"}  # Enable when you add world features
}

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

PERFORMANCE_CONFIG = {
    "enable_gpu": True,
    "gpu_memory_fraction": 0.8,
    "background_processing": True,
    "max_concurrent_thoughts": 3,
    "response_timeout_seconds": 30,
    "enable_caching": True,
    "cache_size_mb": 100
}

# Threading configuration
THREADING_CONFIG = {
    "max_background_threads": 5,
    "thread_timeout_seconds": 10,
    "enable_daemon_threads": True
}

# ============================================================================
# DEBUG AND DEVELOPMENT SETTINGS
# ============================================================================

DEBUG_CONFIG = {
    "debug_mode": False,
    "verbose_logging": True,
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "enable_profiling": False,
    "save_conversation_logs": True,
    "enable_system_diagnostics": True
}

# Development flags
DEV_FLAGS = {
    "skip_model_loading": False,  # Set to True for testing without GPU
    "use_mock_responses": False,  # Set to True for testing UI without LLM
    "enable_experimental_features": False,
    "bypass_safety_checks": False
}

# ============================================================================
# SAFETY AND ETHICS SETTINGS
# ============================================================================

SAFETY_CONFIG = {
    "content_filtering": True,
    "emotional_safety_checks": True,
    "prevent_harmful_outputs": True,
    "max_negative_sentiment": -0.7,
    "enable_value_checking": True,
    "safe_mode": True
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_model_path(model_name: str) -> str:
    """Get full path to model file"""
    return str(MODELS_DIR / model_name)

def get_log_path(log_name: str) -> str:
    """Get full path to log file"""
    return str(LOG_FILES.get(log_name, LOGS_DIR / f"{log_name}.log"))

def get_data_path(data_name: str) -> str:
    """Get full path to data file"""
    return str(DATA_FILES.get(data_name, DATA_DIR / f"{data_name}.json"))

def is_gpu_available() -> bool:
    """Check if GPU is available and enabled"""
    if not PERFORMANCE_CONFIG["enable_gpu"]:
        return False
    
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def get_device() -> str:
    """Get appropriate device (cuda/cpu) based on availability and settings"""
    if is_gpu_available():
        return "cuda"
    return "cpu"

def validate_config():
    """Validate configuration settings"""
    issues = []
    
    # Check if model files exist
    if not (MODELS_DIR / "mistral-7b-instruct-v0.1.Q4_K_M.gguf").exists():
        issues.append("Enrichment model file not found. Run: bash ./download_mistral.sh")
    
    # Check GPU configuration
    if LLM_CONFIG["device"] == "cuda" and not is_gpu_available():
        issues.append("CUDA requested but not available. Consider setting device to 'cpu'")
    
    # Check directories
    for directory in [LOGS_DIR, MODELS_DIR, DATA_DIR]:
        if not directory.exists():
            issues.append(f"Directory missing: {directory}")
    
    return issues

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_config():
    """Initialize configuration and create necessary directories/files"""
    # Create directories
    for directory in [LOGS_DIR, MODELS_DIR, DATA_DIR]:
        directory.mkdir(exist_ok=True)
    
    # Create empty log files if they don't exist
    for log_file in LOG_FILES.values():
        log_file.touch(exist_ok=True)
    
    # Validate configuration
    config_issues = validate_config()
    if config_issues:
        print("⚠️ Configuration Issues Found:")
        for issue in config_issues:
            print(f"  - {issue}")
    
    print(f"✅ Configuration initialized")
    print(f"📁 Base directory: {BASE_DIR}")
    print(f"🖥️ Device: {get_device()}")
    print(f"🧠 Primary model: {ACTIVE_LLM_MODEL}")

# ============================================================================
# RUNTIME CONFIGURATION UPDATES
# ============================================================================

def update_model_config(new_model: str):
    """Update the active model configuration"""
    global ACTIVE_LLM_MODEL
    ACTIVE_LLM_MODEL = new_model
    print(f"🔄 Model updated to: {new_model}")

def enable_world_awareness(api_key: str = None):
    """Enable world awareness features"""
    WORLD_AWARENESS_CONFIG["enabled"] = True
    if api_key:
        API_KEYS["serpapi"] = api_key
    TAB_CONFIG["world"]["enabled"] = True
    print("🌍 World awareness enabled")

def enable_debug_mode():
    """Enable debug mode"""
    DEBUG_CONFIG["debug_mode"] = True
    DEBUG_CONFIG["verbose_logging"] = True
    DEBUG_CONFIG["log_level"] = "DEBUG"
    print("🐛 Debug mode enabled")

def enable_safe_mode():
    """Enable safe mode for testing"""
    DEV_FLAGS["skip_model_loading"] = True
    DEV_FLAGS["use_mock_responses"] = True
    SAFETY_CONFIG["safe_mode"] = True
    print("🛡️ Safe mode enabled - models will not be loaded")

# ============================================================================
# EXPORT CONFIGURATION SUMMARY
# ============================================================================

def get_config_summary() -> dict:
    """Get a summary of current configuration"""
    return {
        "model": ACTIVE_LLM_MODEL,
        "device": get_device(),
        "gpu_available": is_gpu_available(),
        "world_awareness": WORLD_AWARENESS_CONFIG["enabled"],
        "debug_mode": DEBUG_CONFIG["debug_mode"],
        "safe_mode": SAFETY_CONFIG["safe_mode"],
        "directories": {
            "base": str(BASE_DIR),
            "logs": str(LOGS_DIR),
            "models": str(MODELS_DIR),
            "data": str(DATA_DIR)
        }
    }

# Initialize configuration when module is imported
if __name__ != "__main__":
    initialize_config()

# ============================================================================
# COMMAND LINE INTERFACE FOR CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="EchoMind Configuration Manager")
    parser.add_argument("--init", action="store_true", help="Initialize configuration")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--summary", action="store_true", help="Show configuration summary")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--safe", action="store_true", help="Enable safe mode")
    parser.add_argument("--model", type=str, help="Set active model")
    
    args = parser.parse_args()
    
    if args.init:
        initialize_config()
    
    if args.validate:
        issues = validate_config()
        if issues:
            print("❌ Configuration Issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Configuration is valid")
    
    if args.summary:
        import json
        summary = get_config_summary()
        print("📊 Configuration Summary:")
        print(json.dumps(summary, indent=2))
    
    if args.debug:
        enable_debug_mode()
    
    if args.safe:
        enable_safe_mode()
    
    if args.model:
        update_model_config(args.model)
    
    if not any(vars(args).values()):
        # No arguments provided, show help
        parser.print_help()
