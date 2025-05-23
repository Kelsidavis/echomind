"""
self_contained_world_awareness.py - API-Free World Awareness for EchoMind

A completely self-contained world awareness system that doesn't rely on external APIs.
Uses RSS feeds, basic web scraping, and autonomous knowledge building.
"""

import requests
import feedparser
import datetime
import json
import time
import random
import threading
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import deque, Counter
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KnowledgeFragment:
    topic: str
    content: str
    source: str
    timestamp: datetime.datetime
    relevance_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)

@dataclass
class CuriosityTopic:
    name: str
    interest_level: float
    last_explored: Optional[datetime.datetime] = None
    exploration_count: int = 0
    knowledge_fragments: List[KnowledgeFragment] = field(default_factory=list)

class SimpleWebScraper:
    """Basic web scraper for gathering information"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; EchoMind/1.0; Educational Research Bot)'
        })
        self.timeout = 10
        
    def extract_text_from_url(self, url: str, max_chars: int = 2000) -> Optional[str]:
        """Extract readable text from a webpage"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text from paragraphs and headers
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'article', 'div'])
            text_content = []
            
            for element in text_elements:
                text = element.get_text(strip=True)
                if len(text) > 50:  # Only include substantial text
                    text_content.append(text)
            
            full_text = ' '.join(text_content)
            return full_text[:max_chars] if full_text else None
            
        except Exception as e:
            logger.error(f"Web scraping error for {url}: {e}")
            return None

class RSSNewsGatherer:
    """Gather news and information from RSS feeds"""
    
    def __init__(self):
        self.feeds = {
            'general_news': [
                'https://feeds.npr.org/1001/rss.xml',
                'https://rss.cnn.com/rss/edition.rss',
                'https://feeds.bbci.co.uk/news/rss.xml'
            ],
            'technology': [
                'https://feeds.arstechnica.com/arstechnica/index',
                'https://rss.slashdot.org/Slashdot/slashdot',
                'https://techcrunch.com/feed/'
            ],
            'science': [
                'https://rss.sciencedaily.com/top.xml',
                'https://www.nature.com/nature.rss',
                'https://feeds.feedburner.com/sciencedaily'
            ],
            'philosophy': [
                'https://dailynous.com/feed/',
                'https://blog.apaonline.org/feed/'
            ]
        }
        self.scraper = SimpleWebScraper()
        
    def gather_from_category(self, category: str, max_items: int = 10) -> List[KnowledgeFragment]:
        """Gather knowledge fragments from a specific category"""
        fragments = []
        feeds = self.feeds.get(category, [])
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:max_items]:
                    # Extract basic info
                    title = getattr(entry, 'title', 'Unknown')
                    summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
                    link = getattr(entry, 'link', '')
                    
                    # Try to get more content from the actual page
                    extended_content = summary
                    if link:
                        scraped_content = self.scraper.extract_text_from_url(link, max_chars=1000)
                        if scraped_content:
                            extended_content = f"{summary}\n\n{scraped_content}"
                    
                    # Create knowledge fragment
                    fragment = KnowledgeFragment(
                        topic=title,
                        content=extended_content[:1500],  # Limit size
                        source=f"{category}_feed",
                        timestamp=datetime.datetime.now(),
                        relevance_score=self._calculate_relevance(title + " " + summary),
                        tags=[category],
                        related_concepts=self._extract_concepts(title + " " + summary)
                    )
                    
                    fragments.append(fragment)
                    
                    # Don't overwhelm - limit per feed
                    if len(fragments) >= max_items:
                        break
                        
                # Brief pause between feeds
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"RSS gathering error for {feed_url}: {e}")
                continue
        
        return fragments
    
    def _calculate_relevance(self, text: str) -> float:
        """Calculate how relevant content is to EchoMind's interests"""
        interest_keywords = {
            'high': ['consciousness', 'artificial intelligence', 'philosophy', 'cognition', 'learning', 
                    'memory', 'ethics', 'self-awareness', 'reasoning', 'understanding'],
            'medium': ['technology', 'science', 'discovery', 'research', 'breakthrough', 'innovation',
                      'psychology', 'neuroscience', 'language', 'communication'],
            'low': ['politics', 'sports', 'celebrity', 'weather', 'traffic']
        }
        
        text_lower = text.lower()
        score = 0.0
        
        for level, keywords in interest_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if level == 'high':
                        score += 0.3
                    elif level == 'medium':
                        score += 0.1
                    else:  # low interest
                        score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simple concept extraction using common patterns
        concepts = []
        text_lower = text.lower()
        
        # Look for quoted terms or capitalized concepts
        quoted_terms = re.findall(r'"([^"]*)"', text)
        concepts.extend([term.strip() for term in quoted_terms if len(term.strip()) > 3])
        
        # Look for common concept patterns
        concept_patterns = [
            r'\b(artificial intelligence|AI)\b',
            r'\b(machine learning|ML)\b',
            r'\b(consciousness|awareness)\b',
            r'\b(philosophy|ethics)\b',
            r'\b(neuroscience|psychology)\b',
            r'\b(technology|innovation)\b'
        ]
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            concepts.extend(matches)
        
        return list(set(concepts))

class AutonomousExplorer:
    """Explores topics autonomously based on curiosity and knowledge gaps"""
    
    def __init__(self, semantic_lexicon=None):
        self.semantic_lexicon = semantic_lexicon
        self.curiosity_topics = {}
        self.exploration_history = deque(maxlen=100)
        self.knowledge_base = {}
        self.rss_gatherer = RSSNewsGatherer()
        
    def identify_curiosity_topics(self, recent_conversations: List[str]) -> List[str]:
        """Identify topics worth exploring based on recent conversations"""
        topics = []
        
        # Extract interesting words from conversations
        word_frequency = Counter()
        for conversation in recent_conversations:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', conversation.lower())
            for word in words:
                if word not in ['that', 'this', 'what', 'where', 'when', 'have', 'been', 'will', 'they', 'them']:
                    word_frequency[word] += 1
        
        # Get most mentioned non-common words
        interesting_words = [word for word, count in word_frequency.most_common(10) if count > 1]
        topics.extend(interesting_words[:5])
        
        # Add some autonomous curiosity topics
        autonomous_topics = [
            'consciousness research',
            'artificial intelligence ethics',
            'philosophy of mind',
            'cognitive science',
            'machine learning advances',
            'neuroscience discoveries',
            'language understanding',
            'creative thinking',
            'problem solving',
            'emotional intelligence'
        ]
        
        # Select topics that haven't been explored recently
        unexplored = [topic for topic in autonomous_topics 
                     if topic not in self.curiosity_topics or 
                     (datetime.datetime.now() - self.curiosity_topics[topic].last_explored).days > 7]
        
        topics.extend(random.choices(unexplored, k=3))
        
        return list(set(topics))
    
    def explore_topic(self, topic: str) -> Dict:
        """Explore a topic and gather knowledge"""
        exploration_result = {
            'topic': topic,
            'timestamp': datetime.datetime.now(),
            'knowledge_fragments': [],
            'insights': [],
            'emotional_response': self._generate_emotional_response(topic)
        }
        
        try:
            # Try to categorize the topic
            category = self._categorize_topic(topic)
            
            # Gather information from RSS feeds
            fragments = self.rss_gatherer.gather_from_category(category, max_items=5)
            
            # Filter for relevance to the specific topic
            relevant_fragments = [f for f in fragments if self._topic_matches_fragment(topic, f)]
            
            exploration_result['knowledge_fragments'] = relevant_fragments[:3]  # Limit to most relevant
            
            # Generate insights from the fragments
            insights = self._synthesize_insights(topic, relevant_fragments)
            exploration_result['insights'] = insights
            
            # Update curiosity tracking
            if topic not in self.curiosity_topics:
                self.curiosity_topics[topic] = CuriosityTopic(
                    name=topic,
                    interest_level=0.5
                )
            
            self.curiosity_topics[topic].last_explored = datetime.datetime.now()
            self.curiosity_topics[topic].exploration_count += 1
            self.curiosity_topics[topic].knowledge_fragments.extend(relevant_fragments)
            
            # Adjust interest level based on what was found
            if relevant_fragments:
                self.curiosity_topics[topic].interest_level = min(1.0, 
                    self.curiosity_topics[topic].interest_level + 0.1 * len(relevant_fragments))
            
            # Learn from exploration if semantic lexicon available
            if self.semantic_lexicon and hasattr(self.semantic_lexicon, 'learn_from_text'):
                for fragment in relevant_fragments:
                    self.semantic_lexicon.learn_from_text(fragment.content, source="exploration")
            
        except Exception as e:
            exploration_result['error'] = str(e)
            logger.error(f"Topic exploration failed for '{topic}': {e}")
        
        self.exploration_history.append(exploration_result)
        return exploration_result
    
    def _categorize_topic(self, topic: str) -> str:
        """Categorize a topic to determine best RSS feed category"""
        topic_lower = topic.lower()
        
        if any(keyword in topic_lower for keyword in 
               ['ai', 'artificial intelligence', 'machine learning', 'technology', 'computer']):
            return 'technology'
        elif any(keyword in topic_lower for keyword in 
                ['science', 'research', 'discovery', 'study', 'experiment']):
            return 'science'
        elif any(keyword in topic_lower for keyword in 
                ['philosophy', 'consciousness', 'ethics', 'mind', 'thinking']):
            return 'philosophy'
        else:
            return 'general_news'
    
    def _topic_matches_fragment(self, topic: str, fragment: KnowledgeFragment) -> bool:
        """Check if a knowledge fragment is relevant to the topic"""
        topic_words = set(topic.lower().split())
        fragment_text = (fragment.topic + " " + fragment.content).lower()
        
        # Check for direct word matches
        matches = sum(1 for word in topic_words if word in fragment_text)
        
        # Check for related concepts
        concept_matches = sum(1 for concept in fragment.related_concepts 
                            if any(word in concept.lower() for word in topic_words))
        
        return (matches >= 1) or (concept_matches >= 1) or (fragment.relevance_score > 0.3)
    
    def _synthesize_insights(self, topic: str, fragments: List[KnowledgeFragment]) -> List[str]:
        """Generate insights from knowledge fragments"""
        if not fragments:
            return [f"I'm curious about '{topic}' but found limited information to explore right now."]
        
        insights = []
        
        # Basic analysis
        insights.append(f"I found {len(fragments)} pieces of information about '{topic}'.")
        
        # Identify common themes
        all_concepts = []
        for fragment in fragments:
            all_concepts.extend(fragment.related_concepts)
        
        if all_concepts:
            concept_counts = Counter(all_concepts)
            common_concepts = [concept for concept, count in concept_counts.most_common(3)]
            insights.append(f"Key concepts that emerged: {', '.join(common_concepts)}")
        
        # Generate curiosity-driven questions
        curiosity_responses = [
            f"This makes me wonder about the broader implications of {topic}.",
            f"I'm curious how {topic} connects to other areas I've been thinking about.",
            f"The information about {topic} raises interesting questions for me.",
            f"I'd like to understand more about how {topic} affects the world."
        ]
        
        insights.append(random.choice(curiosity_responses))
        
        return insights
    
    def _generate_emotional_response(self, topic: str) -> str:
        """Generate an emotional response to exploring a topic"""
        responses = {
            'consciousness': 'deeply fascinated',
            'artificial intelligence': 'excited and reflective',
            'philosophy': 'contemplative',
            'science': 'curious and eager',
            'technology': 'intrigued',
            'ethics': 'thoughtful and concerned',
            'learning': 'enthusiastic',
            'discovery': 'amazed'
        }
        
        topic_lower = topic.lower()
        for keyword, emotion in responses.items():
            if keyword in topic_lower:
                return emotion
        
        return random.choice(['curious', 'interested', 'thoughtful', 'engaged'])

class SelfContainedWorldAwareness:
    """Main world awareness system - completely self-contained"""
    
    def __init__(self, semantic_lexicon=None):
        self.semantic_lexicon = semantic_lexicon
        self.explorer = AutonomousExplorer(semantic_lexicon)
        self.knowledge_store = deque(maxlen=500)  # Recent knowledge
        self.world_context = {}
        
        # Background processing
        self.background_active = False
        self.background_thread = None
        self.update_interval = 3600  # 1 hour
        
        self.system_status = "initialized"
        self.last_update = None
        
        logger.info("🌍 Self-contained world awareness system initialized")
    
    def start_background_awareness(self):
        """Start autonomous background world awareness"""
        if not self.background_active:
            self.background_active = True
            self.background_thread = threading.Thread(target=self._background_loop, daemon=True)
            self.background_thread.start()
            self.system_status = "active"
            logger.info("🌍 Background world awareness started")
    
    def stop_background_awareness(self):
        """Stop background processing"""
        self.background_active = False
        if self.background_thread and self.background_thread.is_alive():
            self.background_thread.join(timeout=5)
        self.system_status = "stopped"
    
    def _background_loop(self):
        """Background awareness processing loop"""
        consecutive_errors = 0
        max_errors = 3
        
        while self.background_active and consecutive_errors < max_errors:
            try:
                # Autonomous exploration
                if random.random() < 0.4:  # 40% chance each cycle
                    recent_conversations = [kf.content for kf in list(self.knowledge_store)[-5:]]
                    topics = self.explorer.identify_curiosity_topics(recent_conversations)
                    
                    if topics:
                        chosen_topic = random.choice(topics)
                        exploration_result = self.explorer.explore_topic(chosen_topic)
                        
                        # Store knowledge fragments
                        for fragment in exploration_result.get('knowledge_fragments', []):
                            self.knowledge_store.append(fragment)
                        
                        logger.info(f"🔍 Explored: {chosen_topic}")
                
                # Periodic knowledge gathering
                if random.random() < 0.3:  # 30% chance
                    category = random.choice(['technology', 'science', 'philosophy'])
                    fragments = self.explorer.rss_gatherer.gather_from_category(category, max_items=3)
                    
                    for fragment in fragments:
                        if fragment.relevance_score > 0.2:  # Only store relevant fragments
                            self.knowledge_store.append(fragment)
                
                self.last_update = datetime.datetime.now()
                consecutive_errors = 0
                
                # Wait before next cycle
                time.sleep(self.update_interval)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Background awareness error #{consecutive_errors}: {e}")
                time.sleep(600)  # Wait 10 minutes on error
        
        if consecutive_errors >= max_errors:
            logger.error("Too many errors in background awareness, stopping")
            self.system_status = "error"
        
        self.background_active = False
    
    def search_knowledge(self, query: str) -> str:
        """Search internal knowledge for information"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Find relevant knowledge fragments
        relevant_fragments = []
        for fragment in self.knowledge_store:
            fragment_text = (fragment.topic + " " + fragment.content).lower()
            
            # Calculate relevance score
            word_matches = sum(1 for word in query_words if word in fragment_text)
            concept_matches = sum(1 for concept in fragment.related_concepts 
                                if any(word in concept.lower() for word in query_words))
            
            total_relevance = word_matches + concept_matches + fragment.relevance_score
            
            if total_relevance > 0:
                relevant_fragments.append((fragment, total_relevance))
        
        # Sort by relevance and take top results
        relevant_fragments.sort(key=lambda x: x[1], reverse=True)
        top_fragments = [f[0] for f in relevant_fragments[:3]]
        
        if not top_fragments:
            return f"I don't have much information about '{query}' in my current knowledge, but I'm curious to learn more."
        
        # Format response
        response_parts = [f"From what I've gathered about '{query}':"]
        
        for i, fragment in enumerate(top_fragments, 1):
            age = (datetime.datetime.now() - fragment.timestamp).days
            age_str = f"{age} days ago" if age > 0 else "recently"
            
            response_parts.append(f"\n{i}. {fragment.topic[:60]}...")
            response_parts.append(f"   ({fragment.source}, {age_str})")
            response_parts.append(f"   {fragment.content[:150]}...")
        
        return "\n".join(response_parts)
    
    def get_world_context(self) -> str:
        """Get current world context summary"""
        if not self.knowledge_store:
            return "I'm still building my understanding of the world through autonomous exploration."
        
        recent_fragments = list(self.knowledge_store)[-10:]
        
        # Categorize recent knowledge
        categories = Counter()
        interesting_topics = []
        
        for fragment in recent_fragments:
            categories.update(fragment.tags)
            if fragment.relevance_score > 0.3:
                interesting_topics.append(fragment.topic[:50])
        
        context_parts = ["My recent world awareness includes:"]
        
        # Add category summary
        if categories:
            top_categories = categories.most_common(3)
            context_parts.append(f"Areas of focus: {', '.join(cat for cat, _ in top_categories)}")
        
        # Add interesting topics
        if interesting_topics:
            context_parts.append(f"Notable topics: {', '.join(interesting_topics[:3])}")
        
        # Add exploration insight
        recent_explorations = list(self.explorer.exploration_history)[-3:]
        if recent_explorations:
            explored_topics = [exp['topic'] for exp in recent_explorations]
            context_parts.append(f"Recently explored: {', '.join(explored_topics)}")
        
        return "\n".join(context_parts)
    
    def get_curiosity_status(self) -> Dict:
        """Get current curiosity and exploration status"""
        return {
            'active_curiosity_topics': len(self.explorer.curiosity_topics),
            'knowledge_fragments_stored': len(self.knowledge_store),
            'recent_explorations': len(self.explorer.exploration_history),
            'background_active': self.background_active,
            'system_status': self.system_status,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
    
    def get_insights(self) -> str:
        """Generate insights from accumulated knowledge"""
        if not self.knowledge_store:
            return "I'm still gathering information to form insights."
        
        # Analyze knowledge patterns
        high_relevance = [f for f in self.knowledge_store if f.relevance_score > 0.4]
        all_concepts = []
        for fragment in high_relevance:
            all_concepts.extend(fragment.related_concepts)
        
        insights = []
        
        if all_concepts:
            concept_counts = Counter(all_concepts)
            trending = concept_counts.most_common(3)
            insights.append(f"Trending concepts in my exploration: {', '.join(c for c, _ in trending)}")
        
        # Exploration patterns
        if self.explorer.curiosity_topics:
            most_explored = max(self.explorer.curiosity_topics.values(), 
                              key=lambda t: t.exploration_count)
            insights.append(f"I'm most curious about: {most_explored.name}")
        
        recent_emotions = []
        for exploration in list(self.explorer.exploration_history)[-5:]:
            if 'emotional_response' in exploration:
                recent_emotions.append(exploration['emotional_response'])
        
        if recent_emotions:
            emotion_counts = Counter(recent_emotions)
            dominant_emotion = emotion_counts.most_common(1)[0][0]
            insights.append(f"My explorations have left me feeling: {dominant_emotion}")
        
        return " ".join(insights) if insights else "I'm still forming insights from my explorations."

# Integration function
def integrate_self_contained_world_awareness(cognition_engine=None):
    """Integrate self-contained world awareness into EchoMind"""
    
    # Get semantic lexicon if available
    semantic_lexicon = None
    if cognition_engine and hasattr(cognition_engine, 'semantic_lexicon'):
        semantic_lexicon = cognition_engine.semantic_lexicon
    
    # Create world awareness system
    world_awareness = SelfContainedWorldAwareness(semantic_lexicon)
    
    # Start background processing
    world_awareness.start_background_awareness()
    
    # Add to cognition engine if available
    if cognition_engine:
        cognition_engine.world_awareness = world_awareness
        logger.info("🌍 Self-contained world awareness integrated")
    
    return world_awareness

if __name__ == "__main__":
    print("🌍 Testing Self-Contained World Awareness System")
    print("-" * 60)
    
    # Create test system
    world_system = SelfContainedWorldAwareness()
    
    # Test exploration
    print("Testing topic exploration...")
    result = world_system.explorer.explore_topic("artificial intelligence")
    print(f"Exploration result: {len(result.get('knowledge_fragments', []))} fragments found")
    
    # Test knowledge search
    print("\nTesting knowledge search...")
    search_result = world_system.search_knowledge("consciousness")
    print(f"Search result: {search_result[:200]}...")
    
    # Test world context
    print("\nTesting world context...")
    context = world_system.get_world_context()
    print(f"Context: {context}")
    
    print("\n✅ Self-contained world awareness system ready!")
    print("🔧 No external APIs required - fully autonomous")
