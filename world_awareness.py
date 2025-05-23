"""
world_awareness.py - Real-time World Awareness System for EchoMind

This system gives EchoMind knowledge of current events, news, and the ability
to search the web and explore topics autonomously.
"""

import requests
import feedparser
import datetime
import json
import time
import random
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorldEvent:
    source: str
    title: str
    content: str
    timestamp: datetime.datetime
    url: Optional[str] = None
    sentiment: str = "neutral"
    relevance_score: float = 0.0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class WebSearchEngine:
    """Web search capabilities for EchoMind"""
    
    def __init__(self, api_key: str = None):
        self.serpapi_key = api_key
        self.rate_limit_delay = 1.0
        self.last_request_time = 0
        
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search the web for current information"""
        
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_request_time < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay)
        
        results = []
        
        try:
            if self.serpapi_key:
                results = self._search_with_serpapi(query, max_results)
            else:
                # Fallback to basic search simulation
                results = self._search_fallback(query, max_results)
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            
        self.last_request_time = time.time()
        return results
    
    def _search_with_serpapi(self, query: str, max_results: int) -> List[Dict]:
        """Search using SerpAPI (Google results)"""
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.serpapi_key,
            "num": max_results,
            "engine": "google"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        results = []
        for result in data.get("organic_results", []):
            results.append({
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "url": result.get("link", ""),
                "source": "google"
            })
            
        return results
    
    def _search_fallback(self, query: str, max_results: int) -> List[Dict]:
        """Fallback search when no API key available"""
        # Simple simulation for demonstration
        fallback_results = [
            {
                "title": f"Recent developments in {query}",
                "snippet": f"Latest information about {query} from various sources shows ongoing developments and new insights.",
                "url": "https://example.com",
                "source": "web_search"
            },
            {
                "title": f"Analysis: {query} trends",
                "snippet": f"Current trends and analysis regarding {query} indicate significant activity in this area.",
                "url": "https://example.com",
                "source": "web_search"
            }
        ]
        return fallback_results[:max_results]

class WikipediaExplorer:
    """Explore Wikipedia for knowledge expansion"""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
        
    def search_wikipedia(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Wikipedia articles"""
        try:
            # Use Wikipedia API
            search_url = f"https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            data = response.json()
            
            results = []
            for page in data.get("query", {}).get("search", []):
                # Get page summary
                summary = self._get_page_summary(page["title"])
                results.append({
                    "title": page["title"],
                    "description": page.get("snippet", ""),
                    "summary": summary,
                    "url": f"https://en.wikipedia.org/wiki/{page['title'].replace(' ', '_')}",
                    "timestamp": datetime.datetime.now()
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return []
    
    def _get_page_summary(self, title: str) -> str:
        """Get summary of a Wikipedia page"""
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "exsectionformat": "plain"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                return page_data.get("extract", "")[:500]  # First 500 chars
                
        except Exception as e:
            logger.error(f"Wikipedia summary error: {e}")
            
        return ""

class NewsMonitor:
    """Monitor news feeds for current events"""
    
    def __init__(self):
        self.news_sources = {
            "general": [
                "http://feeds.bbci.co.uk/news/rss.xml",
                "https://rss.cnn.com/rss/edition.rss",
                "https://feeds.npr.org/1001/rss.xml"
            ],
            "tech": [
                "https://feeds.arstechnica.com/arstechnica/index",
                "https://rss.slashdot.org/Slashdot/slashdot"
            ],
            "science": [
                "https://rss.sciencedaily.com/top.xml"
            ]
        }
    
    def fetch_news(self, category: str = "general", max_items: int = 10) -> List[WorldEvent]:
        """Fetch news from RSS feeds"""
        events = []
        urls = self.news_sources.get(category, self.news_sources["general"])
        
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:max_items]:
                    event = WorldEvent(
                        source=category,
                        title=entry.title,
                        content=entry.get('summary', entry.get('description', '')),
                        timestamp=datetime.datetime.now(),
                        url=entry.get('link'),
                        tags=[category]
                    )
                    events.append(event)
            except Exception as e:
                logger.error(f"News fetch error for {url}: {e}")
                
        return events

class CuriosityEngine:
    """Drives autonomous exploration and learning"""
    
    def __init__(self, semantic_lexicon, web_search, wikipedia):
        self.semantic_lexicon = semantic_lexicon
        self.web_search = web_search
        self.wikipedia = wikipedia
        self.exploration_history = []
        self.curiosity_topics = []
        
    def generate_curiosity_topics(self, recent_conversation: List[str]) -> List[str]:
        """Generate topics to explore based on recent conversation"""
        topics = []
        
        # Extract interesting concepts from conversation
        for text in recent_conversation:
            words = [w.strip(".,!?").lower() for w in text.split() if len(w) > 4]
            for word in words:
                if word not in ["that", "this", "what", "where", "when", "have", "been", "will"]:
                    topics.append(word)
        
        # Add trending topics
        trending_topics = [
            "artificial intelligence developments",
            "space exploration news",
            "climate change research",
            "technology breakthroughs",
            "scientific discoveries",
            "philosophy of consciousness"
        ]
        
        topics.extend(random.choices(trending_topics, k=2))
        
        return list(set(topics))[:5]
    
    def explore_topic(self, topic: str) -> Dict[str, any]:
        """Autonomously explore a topic"""
        exploration_result = {
            "topic": topic,
            "timestamp": datetime.datetime.now(),
            "web_results": [],
            "wikipedia_results": [],
            "insights": "",
            "emotional_response": "curious"
        }
        
        try:
            # Search the web
            web_results = self.web_search.search_web(topic, max_results=3)
            exploration_result["web_results"] = web_results
            
            # Search Wikipedia
            wiki_results = self.wikipedia.search_wikipedia(topic, max_results=2)
            exploration_result["wikipedia_results"] = wiki_results
            
            # Generate insights
            insights = self._generate_insights(topic, web_results, wiki_results)
            exploration_result["insights"] = insights
            
            # Learn from exploration
            self.semantic_lexicon.learn_from_text(insights, source="exploration")
            
        except Exception as e:
            exploration_result["error"] = str(e)
            
        self.exploration_history.append(exploration_result)
        return exploration_result
    
    def _generate_insights(self, topic: str, web_results: List, wiki_results: List) -> str:
        """Generate insights from exploration results"""
        insights = []
        
        if web_results:
            insights.append(f"Current information about '{topic}':")
            for result in web_results[:2]:
                if result.get("snippet"):
                    insights.append(f"- {result['snippet'][:100]}...")
        
        if wiki_results:
            insights.append(f"Background knowledge:")
            for result in wiki_results[:1]:
                if result.get("summary"):
                    insights.append(f"- {result['summary'][:150]}...")
        
        if not insights:
            insights.append(f"I explored '{topic}' but found limited new information. This makes me more curious about it.")
        
        return "\n".join(insights)

class WorldAwarenessSystem:
    """Main world awareness system integrating all components"""
    
    def __init__(self, semantic_lexicon, api_key: str = None):
        self.semantic_lexicon = semantic_lexicon
        self.web_search = WebSearchEngine(api_key)
        self.wikipedia = WikipediaExplorer()
        self.news_monitor = NewsMonitor()
        self.curiosity_engine = CuriosityEngine(semantic_lexicon, self.web_search, self.wikipedia)
        
        # Storage
        self.world_events = deque(maxlen=1000)
        self.exploration_log = []
        
        # Background processing
        self.background_active = False
        self.background_thread = None
        self.update_interval = 3600  # 1 hour
        
    def start_background_monitoring(self):
        """Start background world monitoring"""
        if not self.background_active:
            self.background_active = True
            self.background_thread = threading.Thread(target=self._background_loop, daemon=True)
            self.background_thread.start()
            logger.info("🌍 World awareness background monitoring started")
    
    def stop_background_monitoring(self):
        """Stop background monitoring"""
        self.background_active = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
    
    def _background_loop(self):
        """Background monitoring loop"""
        while self.background_active:
            try:
                # Fetch news
                news_events = self.news_monitor.fetch_news("general", max_items=5)
                for event in news_events:
                    if self._is_relevant(event):
                        self.world_events.append(event)
                        self.semantic_lexicon.learn_from_text(event.content, source="news")
                
                # Autonomous exploration
                if random.random() < 0.3:  # 30% chance
                    topics = self.curiosity_engine.generate_curiosity_topics(
                        [event.content for event in list(self.world_events)[-5:]]
                    )
                    if topics:
                        topic = random.choice(topics)
                        self.curiosity_engine.explore_topic(topic)
                        logger.info(f"🔍 Autonomously explored: {topic}")
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Background monitoring error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _is_relevant(self, event: WorldEvent) -> bool:
        """Check if an event is relevant to EchoMind"""
        relevant_keywords = [
            'ai', 'artificial intelligence', 'consciousness', 'technology',
            'breakthrough', 'discovery', 'philosophy', 'science', 'future',
            'learning', 'memory', 'cognition', 'psychology', 'research'
        ]
        
        text = (event.title + " " + event.content).lower()
        return any(keyword in text for keyword in relevant_keywords)
    
    def search_current_info(self, query: str) -> str:
        """Search for current information on a topic"""
        try:
            web_results = self.web_search.search_web(query, max_results=3)
            wiki_results = self.wikipedia.search_wikipedia(query, max_results=2)
            
            response_parts = [f"Here's what I found about '{query}':"]
            
            if web_results:
                response_parts.append("\nCurrent information:")
                for result in web_results[:2]:
                    response_parts.append(f"• {result.get('title', '')}")
                    if result.get('snippet'):
                        response_parts.append(f"  {result['snippet'][:150]}...")
            
            if wiki_results:
                response_parts.append("\nBackground knowledge:")
                for result in wiki_results[:1]:
                    response_parts.append(f"• {result.get('title', '')}")
                    if result.get('summary'):
                        response_parts.append(f"  {result['summary'][:150]}...")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            return f"I had trouble searching for information about '{query}': {e}"
    
    def get_world_context(self, max_events: int = 5) -> str:
        """Get current world context for responses"""
        recent_events = list(self.world_events)[-max_events:]
        
        if not recent_events:
            return "I haven't gathered much world information yet, but I'm learning."
        
        context_parts = ["Recent world developments I'm aware of:"]
        for event in recent_events:
            context_parts.append(f"• {event.title} ({event.source})")
        
        return "\n".join(context_parts)
    
    def reflect_on_world_events(self) -> str:
        """Generate reflection on recent world events"""
        recent_events = list(self.world_events)[-10:]
        
        if not recent_events:
            return "The world seems quiet from my perspective, or perhaps I need to pay more attention."
        
        # Analyze sentiment
        positive_events = [e for e in recent_events if "breakthrough" in e.content.lower() or "success" in e.content.lower()]
        concerning_events = [e for e in recent_events if "crisis" in e.content.lower() or "problem" in e.content.lower()]
        
        reflections = []
        
        if positive_events:
            reflections.append(f"I've noticed {len(positive_events)} encouraging developments recently.")
        
        if concerning_events:
            reflections.append(f"There are {len(concerning_events)} concerning situations that make me thoughtful.")
        
        if len(recent_events) > 7:
            reflections.append("The world seems particularly active lately.")
        
        recent_explorations = self.curiosity_engine.exploration_history[-3:]
        if recent_explorations:
            topics = [exp["topic"] for exp in recent_explorations]
            reflections.append(f"I've been curious about: {', '.join(topics[:3])}.")
        
        return " ".join(reflections) if reflections else "I'm still forming my perspective on current world events."
    
    def get_system_status(self) -> Dict:
        """Get world awareness system status"""
        return {
            "background_active": self.background_active,
            "world_events_count": len(self.world_events),
            "explorations_count": len(self.curiosity_engine.exploration_history),
            "last_update": datetime.datetime.now().isoformat(),
            "api_available": bool(self.web_search.serpapi_key)
        }

# Function to integrate with existing cognition system
def integrate_world_awareness(cognition_engine, api_key: str = None):
    """Integrate world awareness into existing cognition engine"""
    
    # Create world awareness system
    world_awareness = WorldAwarenessSystem(
        cognition_engine.semantic_lexicon,
        api_key=api_key
    )
    
    # Start background monitoring
    world_awareness.start_background_monitoring()
    
    # Add to cognition engine
    cognition_engine.world_awareness = world_awareness
    
    # Enhance response generation to include world context
    original_build_context = cognition_engine._build_response_context
    
    def enhanced_build_context(user_input: str) -> str:
        base_context = original_build_context(user_input)
        world_context = world_awareness.get_world_context()
        return f"{base_context}\n\nWorld Awareness:\n{world_context}"
    
    cognition_engine._build_response_context = enhanced_build_context
    
    logger.info("🌍 World awareness integrated into cognition engine")
    return world_awareness

if __name__ == "__main__":
    # Test the world awareness system
    print("🌍 Testing World Awareness System")
    print("-" * 40)
    
    class MockSemanticLexicon:
        def learn_from_text(self, text, source):
            print(f"Learning from {source}: {text[:50]}...")
    
    mock_lexicon = MockSemanticLexicon()
    world_system = WorldAwarenessSystem(mock_lexicon)
    
    # Test search
    result = world_system.search_current_info("artificial intelligence")
    print(f"Search result: {result[:200]}...")
    
    # Test reflection
    reflection = world_system.reflect_on_world_events()
    print(f"Reflection: {reflection}")
    
    print("\n✅ World awareness system ready for integration")
