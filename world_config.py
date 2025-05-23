# World Awareness Configuration
# Add this to your config.py or create world_config.py

WORLD_AWARENESS_CONFIG = {
    "enabled": True,
    "api_key": None,  # Get free key from serpapi.com
    "update_interval_hours": 1,
    "max_events_stored": 1000,
    "autonomous_exploration": True,
    "news_categories": ["general", "tech", "science"]
}

# To get a free API key:
# 1. Go to https://serpapi.com/
# 2. Sign up for free account
# 3. Get your API key (100 free searches/month)
# 4. Set WORLD_AWARENESS_CONFIG["api_key"] = "your_key_here"