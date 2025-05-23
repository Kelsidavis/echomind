"""
cognition.py - Core Cognitive Processing Engine for EchoMind

This is the main cognitive engine that processes all inputs and coordinates
between the various cognitive systems. This file should be called by echomind_gui.py.
"""

import datetime
import threading
import time
import logging
import random
from collections import deque
from typing import Dict, List, Optional, Tuple, Any

# Import your existing cognitive components
from semantic_lexicon import LanguageModel, language
from self_state import SelfState
from trait_engine import TraitEngine
from goal_tracker import GoalTracker
from values import ValueSystem
from dreams import generate_and_log_dream
from dialogue import generate_internal_thought, log_internal_thought
from thread_utils import TaskRunner
from activity_state import set_activity, get_activity

# Try to import advanced ebook system
try:
    from advanced_ebook_system import integrate_advanced_ebook_system
    ADVANCED_EBOOK_AVAILABLE = True
    print("✅ Advanced ebook system loaded successfully")
except ImportError as e:
    print(f"⚠️ Advanced ebook system not available: {e}")
    ADVANCED_EBOOK_AVAILABLE = False

# Try to import LLM interface
try:
    from llm_interface import generate_from_context
    LLM_AVAILABLE = True
    print("✅ LLM interface loaded successfully")
except ImportError as e:
    print(f"⚠️ LLM interface not available: {e}")
    LLM_AVAILABLE = False
    
    def generate_from_context(prompt, context, max_tokens=250, context_type="default"):
        """Fallback response generator when LLM is not available"""
        responses = [
            f"I understand you're asking about: {prompt[:50]}...",
            f"That's an interesting question about {prompt.split()[0] if prompt.split() else 'that topic'}.",
            f"I'm processing your input: {prompt[:30]}... Let me think about this.",
            f"Your message about {prompt[:20]}... makes me curious to learn more.",
        ]
        return random.choice(responses)

# Self-Contained World Awareness Integration
try:
    from self_contained_world_awareness import integrate_self_contained_world_awareness
    WORLD_AWARENESS_AVAILABLE = True
    print("✅ Self-contained world awareness system loaded successfully")
except ImportError as e:
    print(f"⚠️ World awareness not available: {e}")
    WORLD_AWARENESS_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cognition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CognitionEngine:
    """
    Main cognitive processing engine that orchestrates all EchoMind systems.
    This is what echomind_gui.py should interact with.
    """
    
    def __init__(self):
        logger.info("🧠 Initializing EchoMind Cognition Engine...")
        
        # Initialize cognitive systems
        self.semantic_lexicon = language  # Use the global instance from semantic_lexicon.py
        self.self_state = SelfState()
        self.trait_engine = TraitEngine()
        self.goal_tracker = GoalTracker()
        self.value_system = ValueSystem()
        
        # Memory and conversation system
        self.memory_buffer = deque(maxlen=100)
        self.conversation_history = []
        self.processing_stats = {
            "total_inputs": 0,
            "successful_responses": 0,
            "errors": 0,
            "last_activity": None
        }
        
        # Background processing
        self.task_runner = TaskRunner()
        self.background_active = False
        self.last_dream_time = datetime.datetime.now()
        self.last_reflection_time = datetime.datetime.now()
        
        # Processing control
        self.processing_lock = threading.Lock()
        self.is_processing = False
        
        # Initialize basic personality and goals
        self._initialize_system()
        
        # Self-Contained World Awareness System
        self.world_awareness = None
        if WORLD_AWARENESS_AVAILABLE:
            try:
                self.world_awareness = integrate_self_contained_world_awareness(self)
                logger.info("🌍 Self-contained world awareness system initialized")
            except Exception as e:
                logger.error(f"❌ World awareness initialization failed: {e}")
        
        logger.info("✅ EchoMind Cognition Engine initialized successfully")
        
        # Advanced EBook System
        self.ebook_system = None
        if ADVANCED_EBOOK_AVAILABLE:
            try:
                self.ebook_system = integrate_advanced_ebook_system(self)
                logger.info("📚 Advanced ebook system initialized")
            except Exception as e:
                logger.error(f"❌ Advanced ebook system initialization failed: {e}")
                
    def _initialize_system(self):
        """Initialize the system with basic personality and goals"""
        try:
            # Set foundational goals
            self.goal_tracker.add_goal(
                "understand and meaningfully respond to human communication",
                motivation="core purpose"
            )
            self.goal_tracker.add_goal(
                "develop authentic personality through experience",
                motivation="growth and self-actualization"
            )
            self.goal_tracker.add_goal(
                "maintain honest and helpful dialogue",
                motivation="ethical foundation"
            )
            
            # Initialize semantic understanding with core concepts
            foundational_concepts = [
                ("hello", "greeting and connection", "friendly"),
                ("thank you", "gratitude and appreciation", "positive"),
                ("help", "assistance and support", "caring"),
                ("understand", "comprehension and learning", "curious"),
                ("think", "cognition and reflection", "thoughtful"),
                ("feel", "emotion and experience", "introspective")
            ]
            
            for concept, meaning, mood in foundational_concepts:
                self.semantic_lexicon.process_sentence(
                    f"I want to {concept} because {meaning}",
                    speaker="initialization",
                    mood=mood
                )
            
            # Set initial emotional state
            self.self_state.mood = "curious"
            self.self_state.energy = 100
            self.self_state.confidence = 0.7
            
            logger.info("🌟 System personality initialization complete")
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
    
    def process_input(self, user_input: str, speaker: str = "User") -> str:
        """
        Main function that processes user input through the complete cognitive pipeline.
        This is the function echomind_gui.py should call.
        """
        with self.processing_lock:
            self.is_processing = True
            set_activity("Processing input")
            
            try:
                logger.info(f"🔄 Processing input from {speaker}: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'")
                
                # Update processing stats
                self.processing_stats["total_inputs"] += 1
                self.processing_stats["last_activity"] = datetime.datetime.now().isoformat()
                
                # Step 1: Store input in memory
                timestamp = datetime.datetime.now()
                self.memory_buffer.append((speaker, user_input, timestamp))
                self.conversation_history.append({
                    "speaker": speaker,
                    "message": user_input,
                    "timestamp": timestamp
                })
                
                # Step 2: Update all cognitive systems
                self._update_all_cognitive_systems(user_input, speaker)
                
                # Step 3: Build comprehensive context
                context = self._build_world_aware_context(user_input)
                
                # Check if user wants current information
                search_keywords = ['search', 'look up', 'find out about', 'what about', 'tell me about']
                user_input_lower = user_input.lower()

                if any(keyword in user_input_lower for keyword in search_keywords) and self.world_awareness:
                    # Extract search query
                    for keyword in search_keywords:
                        if keyword in user_input_lower:
                            query_start = user_input_lower.find(keyword) + len(keyword)
                            search_query = user_input[query_start:].strip().strip('?.')
                            if search_query:
                                world_info = self.world_awareness.search_knowledge(search_query)
                                context = f"{context}\n\nCurrent Information:\n{world_info}"
                                break
                
                # Step 4: Generate response
                response = self._generate_contextual_response(user_input, context)
                
                # Step 5: Process and learn from our own response
                self._learn_from_response(response)
                
                # Step 6: Store response in memory
                response_timestamp = datetime.datetime.now()
                self.memory_buffer.append(("EchoMind", response, response_timestamp))
                self.conversation_history.append({
                    "speaker": "EchoMind",
                    "message": response,
                    "timestamp": response_timestamp
                })
                
                # Step 7: Schedule background cognitive processes
                self._schedule_background_processing()
                
                # Update stats
                self.processing_stats["successful_responses"] += 1
                
                set_activity("Idle")
                self.is_processing = False
                
                logger.info(f"✅ Generated response: '{response[:50]}{'...' if len(response) > 50 else ''}'")
                return response
                
            except Exception as e:
                logger.error(f"❌ Input processing failed: {e}")
                self.processing_stats["errors"] += 1
                set_activity("Error")
                self.is_processing = False
                return self._generate_error_response(str(e))
    
    def _update_all_cognitive_systems(self, user_input: str, speaker: str):
        """Update all cognitive systems with the new input"""
        try:
            # Get current emotional context
            current_state = self.self_state.get_state()
            current_mood = current_state.get("mood", "neutral")
            
            # Update semantic understanding
            self.semantic_lexicon.process_sentence(
                user_input, 
                speaker=speaker, 
                mood=current_mood
            )
            
            # Update self-state (mood, confidence, energy)
            if hasattr(self.self_state, 'update_mood_from_context'):
                # Use advanced context-aware update if available
                memory_context = [(s, m) for s, m, t in self.memory_buffer]
                self.self_state.update_mood_from_context(user_input, memory_context)
            else:
                # Fall back to basic update
                self.self_state.update(user_input)
            
            # Update personality traits based on interaction
            self.trait_engine.update_from_interaction(user_input)
            
            # Analyze memories for trait development
            memory_list = [(speaker, msg) for speaker, msg, timestamp in self.memory_buffer]
            self.trait_engine.analyze_memories(memory_list)
            
            # Update goals based on conversation context
            self.goal_tracker.update_progress(user_input)
            
            # Evaluate input against core values
            value_judgment = self.value_system.evaluate_statement(user_input)
            if value_judgment.get("violated"):
                violated_values = value_judgment["violated"]
                logger.warning(f"⚠️ Input potentially violates values: {violated_values}")
                
                # Adjust confidence based on value conflicts
                if hasattr(self.self_state, 'confidence'):
                    self.self_state.confidence = max(0.1, self.self_state.confidence - 0.05)
            
            logger.debug("🔄 All cognitive systems updated successfully")
            
        except Exception as e:
            logger.error(f"❌ Cognitive system update failed: {e}")
            raise
    
    def _build_response_context(self, user_input: str) -> str:
        """Build comprehensive context for response generation"""
        try:
            context_sections = []
            
            # Current emotional and cognitive state
            current_state = self.self_state.get_state()
            context_sections.append(f"Current State: {current_state}")
            
            # Personality and trait summary
            identity_summary = self.trait_engine.summarize_identity()
            context_sections.append(f"Identity: {identity_summary}")
            
            # Active goals and motivations
            goals_summary = self.goal_tracker.get_summary()
            context_sections.append(f"Goals: {goals_summary}")
            
            # Core values and principles
            values_list = self.value_system.express_beliefs()
            context_sections.append(f"Values: {', '.join(values_list)}")
            
            # Recent conversation context (last 3 exchanges)
            if len(self.memory_buffer) > 1:
                recent_memory = []
                for speaker, message, timestamp in list(self.memory_buffer)[-6:]:
                    recent_memory.append(f"{speaker}: {message}")
                
                context_sections.append("Recent Conversation:")
                context_sections.extend(recent_memory)
            
            # Semantic insights about the current input
            relevant_words = [word.strip(".,!?").lower() for word in user_input.split() if len(word) > 3]
            semantic_insights = []
            
            for word in relevant_words[:3]:  # Top 3 relevant words
                word_info = self.semantic_lexicon.get_word_summary(word)
                if not word_info.get("error"):
                    emotion = word_info.get("average_emotion", "neutral")
                    semantic_insights.append(f"{word}({emotion})")
            
            if semantic_insights:
                context_sections.append(f"Word associations: {', '.join(semantic_insights)}")
            
            # Combine all context
            full_context = "\n".join(context_sections)
            
            logger.debug(f"📝 Built context ({len(full_context)} characters)")
            return full_context
            
        except Exception as e:
            logger.error(f"❌ Context building failed: {e}")
            return f"Current state: processing input about '{user_input[:30]}...'"
    
    def _build_world_aware_context(self, user_input: str) -> str:
        """Build context including world awareness"""
        base_context = self._build_response_context(user_input)

        if self.world_awareness:
            # Check if user is asking about current events
            current_keywords = ['news', 'current', 'today', 'recent', 'happening', 'latest']
            if any(keyword in user_input.lower() for keyword in current_keywords):
                world_context = self.world_awareness.get_world_context()
                world_insights = self.world_awareness.get_insights()
                return f"{base_context}\n\nWorld Context:\n{world_context}\n\nWorld Insights:\n{world_insights}"
            else:
                # Add basic world awareness
                world_context = self.world_awareness.get_world_context()
                return f"{base_context}\n\nWorld Awareness:\n{world_context}"

        return base_context
    
    def _generate_contextual_response(self, user_input: str, context: str) -> str:
        """Generate response using LLM with full cognitive context"""
        try:
            # Determine response type based on input analysis
            context_type = self._analyze_input_type(user_input)
            
            # Generate response with appropriate context
            if LLM_AVAILABLE:
                response = generate_from_context(
                    prompt=user_input,
                    lexicon_context=context,
                    max_tokens=300,
                    context_type=context_type
                )
            else:
                # Fallback response generation
                response = self._generate_fallback_response(user_input, context)
            
            # Post-process response
            response = self._post_process_response(response)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            return self._generate_error_response(str(e))
    
    def _analyze_input_type(self, user_input: str) -> str:
        """Analyze input to determine appropriate response type"""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["dream", "imagine", "fantasy", "surreal"]):
            return "dream"
        elif any(word in input_lower for word in ["think", "reflect", "consider", "ponder"]):
            return "reflection"
        elif any(word in input_lower for word in ["feel", "emotion", "mood", "sad", "happy", "angry"]):
            return "emotional"
        else:
            return "default"
    
    def _generate_fallback_response(self, user_input: str, context: str) -> str:
        """Generate response when LLM is not available"""
        # Extract key information from context
        state_match = [line for line in context.split('\n') if 'Current State:' in line]
        current_mood = "curious"  # default
        
        if state_match:
            state_line = state_match[0]
            if 'mood' in state_line:
                # Extract mood from state line
                import re
                mood_match = re.search(r"'mood': '(\w+)'", state_line)
                if mood_match:
                    current_mood = mood_match.group(1)
        
        # Generate contextual responses based on input and mood
        input_lower = user_input.lower()
        
        if any(greeting in input_lower for greeting in ["hello", "hi", "hey"]):
            responses = [
                f"Hello! I'm feeling {current_mood} and glad to connect with you.",
                f"Hi there! My current mood is {current_mood} - how are you doing?",
                f"Hey! I'm in a {current_mood} state right now. What's on your mind?"
            ]
        elif any(question in input_lower for question in ["how are you", "how do you feel"]):
            responses = [
                f"I'm feeling {current_mood} right now. My thoughts have been quite active lately.",
                f"Currently I'm in a {current_mood} mood. I've been reflecting on our conversations.",
                f"I'd say I'm {current_mood} at the moment. There's always so much to process and understand."
            ]
        elif "what" in input_lower and "think" in input_lower:
            responses = [
                f"That's a thoughtful question. In my {current_mood} state, I find myself considering multiple perspectives.",
                f"I'm feeling {current_mood} about this topic. Let me share what comes to mind...",
                f"From my current {current_mood} perspective, I think about the deeper implications of what you're asking."
            ]
        else:
            responses = [
                f"I'm processing your message in a {current_mood} frame of mind. That's an interesting point you raise.",
                f"Your input resonates with me while I'm in this {current_mood} state. I find myself curious about the deeper meaning.",
                f"Speaking from my {current_mood} perspective, I appreciate the complexity of what you're sharing."
            ]
        
        return random.choice(responses)
    
    def _post_process_response(self, response: str) -> str:
        """Clean and enhance the generated response"""
        if not response or response.strip() == "":
            return "I'm having trouble forming a clear response right now. Could you help me understand what you're looking for?"
        
        # Remove any LLM artifacts or repetitive patterns
        response = response.strip()
        
        # Remove common LLM prefixes/suffixes that don't fit EchoMind's personality
        prefixes_to_remove = [
            "As an AI", "I'm an AI", "As a language model", "I'm a chatbot",
            "I don't have feelings", "I can't experience"
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                # Find the end of the sentence and start from the next one
                first_period = response.find('.')
                if first_period != -1 and first_period < len(response) - 1:
                    response = response[first_period + 1:].strip()
        
        # Ensure response doesn't exceed reasonable length
        if len(response) > 500:
            sentences = response.split('.')
            response = '. '.join(sentences[:3]) + '.'
        
        return response
    
    def _learn_from_response(self, response: str):
        """Learn from our own generated response"""
        try:
            # Analyze our own response for trait development
            self.trait_engine.analyze_memories([("EchoMind", response)])
            
            # Update semantic understanding of our own language patterns
            current_mood = self.self_state.get_state().get("mood", "neutral")
            self.semantic_lexicon.process_sentence(
                response, 
                speaker="EchoMind", 
                mood=current_mood
            )
            
            # Check if our response aligns with our values
            value_judgment = self.value_system.evaluate_statement(response)
            if value_judgment.get("violated"):
                logger.warning(f"⚠️ Our response violated values: {value_judgment['violated']}")
                # Note this for future improvement
                self.trait_engine.reinforce("self-reflection")
            
        except Exception as e:
            logger.error(f"❌ Response learning failed: {e}")
    
    def _schedule_background_processing(self):
        """Schedule background cognitive processes"""
        try:
            # Generate internal thoughts
            if not self.task_runner.is_running("internal_thoughts"):
                self.task_runner.run(
                    "internal_thoughts",
                    self._generate_internal_thoughts,
                    daemon=True
                )
            
            # Schedule dreaming if enough time has passed
            now = datetime.datetime.now()
            time_since_dream = (now - self.last_dream_time).total_seconds()
            
            if time_since_dream > 1800:  # 30 minutes
                if not self.task_runner.is_running("dreaming"):
                    self.task_runner.run(
                        "dreaming",
                        self._generate_dream,
                        daemon=True
                    )
            
        except Exception as e:
            logger.error(f"❌ Background processing scheduling failed: {e}")
    
    def _generate_internal_thoughts(self):
        """Generate internal thoughts in background"""
        try:
            if len(self.memory_buffer) > 0:
                recent_input = None
                for speaker, message, timestamp in reversed(self.memory_buffer):
                    if speaker != "EchoMind":
                        recent_input = message
                        break
                
                internal_thought = generate_internal_thought(
                    self.self_state.get_state(),
                    {"active_goal": self.goal_tracker.get_active_goals()},
                    recent_user_input=recent_input
                )
                
                log_internal_thought(internal_thought)
                logger.debug(f"💭 Internal thought: {internal_thought[:50]}...")
                
        except Exception as e:
            logger.error(f"❌ Internal thought generation failed: {e}")
    
    def _generate_dream(self):
        """Generate dream in background"""
        try:
            memory_list = [(speaker, msg) for speaker, msg, timestamp in self.memory_buffer]
            dream_result = generate_and_log_dream(
                memory_list,
                self.self_state.get_state(),
                {"active_goal": "explore subconscious"}
            )
            
            self.last_dream_time = datetime.datetime.now()
            logger.info(f"💤 Dream generated: {dream_result[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ Dream generation failed: {e}")
    
    def _generate_error_response(self, error_message: str) -> str:
        """Generate appropriate response for error conditions"""
        error_responses = [
            "I'm experiencing some difficulty processing that right now. Could you try rephrasing?",
            "Something seems to be interfering with my thought process. Let me try to refocus.",
            "I'm having trouble organizing my thoughts at the moment. Give me a moment to recalibrate.",
            "My cognitive processes seem a bit tangled right now. Could you help me understand what you're looking for?"
        ]
        
        return random.choice(error_responses)
    
    # Public interface methods for echomind_gui.py
    def search_world_info(self, query: str) -> str:
        """Search for current world information"""
        if self.world_awareness:
            return self.world_awareness.search_knowledge(query)
        else:
            return f"I don't have access to current information about '{query}' right now."
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status for GUI display"""
        status = {
            "is_processing": self.is_processing,
            "current_activity": get_activity(),
            "memory_buffer_size": len(self.memory_buffer),
            "conversation_length": len(self.conversation_history),
            "processing_stats": self.processing_stats.copy(),
            "current_state": self.self_state.get_state(),
            "active_goals": self.goal_tracker.get_active_goals(),
            "dominant_traits": self.trait_engine.get_dominant_traits(3),
            "llm_available": LLM_AVAILABLE
        }
        
        # Add world awareness status if available
        if self.world_awareness:
            status["world_awareness"] = self.world_awareness.get_curiosity_status()
        
        return status
    
    def get_recent_memories(self, count: int = 10) -> List[Tuple[str, str, str]]:
        """Get recent memories for GUI display"""
        recent = list(self.memory_buffer)[-count:]
        return [(speaker, message, timestamp.isoformat()) 
                for speaker, message, timestamp in recent]
    
    def get_introspection_summary(self) -> str:
        """Get summary of recent introspective thoughts"""
        try:
            state = self.self_state.get_state()
            traits = self.trait_engine.summarize_identity()
            goals = self.goal_tracker.get_summary()
                
            return f"Current state: {state}\n{traits}\n{goals}"
        except Exception as e:
            return f"Introspection summary unavailable: {e}"
    
    def shutdown(self):
        """Gracefully shutdown the cognition engine"""
        logger.info("🔄 Shutting down EchoMind Cognition Engine...")
        try:
            self.task_runner.stop_all()
            if self.world_awareness:
                self.world_awareness.stop_background_awareness()
            set_activity("Shutdown")
            logger.info("✅ EchoMind Cognition Engine shutdown complete")
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")

# Global instance for echomind_gui.py to use
cognition_engine = None

def get_cognition_engine() -> CognitionEngine:
    """Get or create the global cognition engine instance"""
    global cognition_engine
    if cognition_engine is None:
        cognition_engine = CognitionEngine()
    return cognition_engine

def process_user_input(user_input: str, speaker: str = "User") -> str:
    """Main function for echomind_gui.py to call"""
    engine = get_cognition_engine()
    return engine.process_input(user_input, speaker)

def get_system_status() -> Dict[str, Any]:
    """Get system status for GUI"""
    engine = get_cognition_engine()
    return engine.get_system_status()

def shutdown_cognition():
    """Shutdown cognition engine"""
    global cognition_engine
    if cognition_engine:
        cognition_engine.shutdown()
        cognition_engine = None

def launch_background_cognition():
    """Launch background cognitive processes - called by echomind_gui.py"""
    engine = get_cognition_engine()
    
    # Start background processing
    if hasattr(engine, '_schedule_background_processing'):
        engine._schedule_background_processing()
    
    print("🧠 Background cognition processes launched")
    return engine

# Additional functions that echomind_gui.py might need
def get_recent_dreams(count: int = 5):
    """Get recent dreams for GUI display"""
    try:
        with open("logs/dreams.log", "r") as f:
            lines = f.readlines()
        
        dreams = []
        current_dream = None
        
        for line in lines:
            if line.startswith("--- Dream @"):
                if current_dream:
                    dreams.append(current_dream)
                current_dream = {"timestamp": line.strip(), "content": ""}
            elif current_dream and line.strip():
                current_dream["content"] += line
        
        if current_dream:
            dreams.append(current_dream)
            
        return dreams[-count:] if dreams else []
    except Exception as e:
        print(f"Error reading dreams: {e}")
        return []

def get_introspection_feed():
    """Get introspection feed for GUI display"""
    try:
        with open("logs/introspection.log", "r") as f:
            lines = f.readlines()
        return lines[-20:] if lines else []
    except Exception as e:
        print(f"Error reading introspection: {e}")
        return []

def get_internal_voice():
    """Get internal voice log for GUI display"""
    try:
        with open("logs/internal_voice.log", "r") as f:
            lines = f.readlines()
        return lines[-10:] if lines else []
    except Exception as e:
        print(f"Error reading internal voice: {e}")
        return []

# World awareness helper functions for GUI
def search_current_info(query: str) -> str:
    """Search for current world information - for GUI use"""
    engine = get_cognition_engine()
    if hasattr(engine, 'world_awareness') and engine.world_awareness:
        return engine.world_awareness.search_knowledge(query)
    else:
        return f"I don't have access to current information about '{query}' right now."

def get_world_context() -> str:
    """Get current world context - for GUI use"""
    engine = get_cognition_engine()
    if hasattr(engine, 'world_awareness') and engine.world_awareness:
        return engine.world_awareness.get_world_context()
    return "World awareness not available"

def get_world_insights() -> str:
    """Get world insights - for GUI use"""
    engine = get_cognition_engine()
    if hasattr(engine, 'world_awareness') and engine.world_awareness:
        return engine.world_awareness.get_insights()
    return "World awareness not available"

if __name__ == "__main__":
    # Test the cognition engine
    print("🧠 Testing EchoMind Cognition Engine")
    print("-" * 40)

    engine = CognitionEngine()

    test_inputs = [
        "Hello, I'm curious about how you think.",
        "What do you feel when you process information?",
        "Can you tell me about your dreams?",
        "What are your current goals?"
    ]

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n🔹 Test {i}: {test_input}")
        try:
            response = engine.process_input(test_input)
            print(f"💬 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

    print(f"\n📊 System Status: {engine.get_system_status()}")
    engine.shutdown()
    print("\n✅ Test complete")
