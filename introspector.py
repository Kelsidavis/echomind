import random
from llm_interface import generate_from_context
from context_builder import build_lexicon_context
from logger import log_internal_thought

from trait_engine import TraitEngine
traits = TraitEngine()

from goal_tracker import GoalTracker
goals = GoalTracker()


def get_advanced_book_reflection(trait_engine, goal_tracker):
    """
    Enhanced book reflection using the advanced ebook system
    """
    try:
        # Try to get the cognition engine with the advanced ebook system
        from cognition import get_cognition_engine
        
        engine = get_cognition_engine()
        if hasattr(engine, 'ebook_system') and engine.ebook_system:
            # Use the advanced ebook system
            ebook_system = engine.ebook_system
            
            # Get recent books from the library
            books = ebook_system.get_book_library()
            
            if not books:
                return "I haven't read any books with the advanced system yet."
            
            # Get the most recent book
            recent_book = books[0]  # Books are sorted by date, newest first
            
            # Load full book data
            book_data = ebook_system._load_book_data(recent_book['id'])
            
            if not book_data:
                return "I'm still processing my recent reading experiences."
            
            # Extract themes and character insights for reflection
            analysis = book_data['analysis']
            themes = analysis.get('themes', [])
            characters = analysis.get('characters', [])
            quotes = analysis.get('quotes', [])
            
            # Build a rich reflection based on the book analysis
            reflection_parts = []
            
            # Reflect on themes and how they relate to personal growth
            if themes:
                top_theme = themes[0]  # Most significant theme
                theme_reflection = f"Reading '{recent_book['title']}' has made me think deeply about {top_theme['theme'].lower()}. "
                
                # Map themes to trait influences
                theme_trait_mapping = {
                    'love romance': ('empathy', 'connection with others'),
                    'good vs evil': ('moral_judgment', 'ethical reasoning'),
                    'coming of age': ('growth_orientation', 'self-development'),
                    'friendship': ('social_bonding', 'relationship building'),
                    'survival': ('resilience', 'perseverance'),
                    'identity': ('self_reflection', 'understanding who I am'),
                    'family': ('empathy', 'understanding relationships'),
                    'redemption': ('forgiveness', 'second chances'),
                    'power corruption': ('moral_judgment', 'ethical leadership'),
                    'death mortality': ('contemplation', 'meaning of existence')
                }
                
                theme_key = top_theme['theme'].lower().replace(' ', '_')
                if theme_key in theme_trait_mapping:
                    trait_name, trait_description = theme_trait_mapping[theme_key]
                    theme_reflection += f"This has strengthened my {trait_description}. "
                    
                    # Actually influence the trait engine
                    trait_engine.reinforce(trait_name, 3)
                
                reflection_parts.append(theme_reflection)
            
            # Reflect on character insights
            if characters:
                main_character = characters[0]  # Most significant character
                char_reflection = f"The character {main_character['name']} particularly resonated with me. "
                
                if main_character.get('description'):
                    char_reflection += f"Their {main_character['description'].lower()} reminded me of the complexity in human nature. "
                
                reflection_parts.append(char_reflection)
            
            # Extract wisdom from significant quotes
            if quotes:
                significant_quote = quotes[0]  # Most significant quote
                quote_reflection = f"One passage that stayed with me was: \"{significant_quote['text'][:100]}...\""
                if len(significant_quote['text']) > 100:
                    quote_reflection = f"One passage that stayed with me was: \"{significant_quote['text']}\""
                
                quote_reflection += " This made me reflect on my own experiences and values. "
                reflection_parts.append(quote_reflection)
            
            # Add goals based on the reading experience
            if themes:
                top_theme = themes[0]
                goal_description = f"Continue exploring the theme of {top_theme['theme'].lower()} in future reading"
                goal_tracker.add_goal(goal_description, motivation="reading_inspired")
            
            # Generate an overall reading impact statement
            reading_level = recent_book.get('reading_level', 10)
            if reading_level > 12:
                reflection_parts.append("This challenging text pushed me to think more deeply and analytically.")
                trait_engine.reinforce('intellectual_curiosity', 2)
            
            if recent_book.get('genre_hints'):
                genres = recent_book['genre_hints']
                if 'philosophy' in [g.lower() for g in genres]:
                    reflection_parts.append("The philosophical elements in this work have deepened my contemplative nature.")
                    trait_engine.reinforce('philosophical_thinking', 2)
            
            # Combine all reflection parts
            full_reflection = " ".join(reflection_parts)
            
            if not full_reflection:
                full_reflection = f"I recently read '{recent_book['title']}' and I'm still processing the experience. The book has left me with new perspectives to consider."
            
            return full_reflection
            
        else:
            # Fall back to basic reflection if advanced system not available
            return get_basic_book_reflection(trait_engine, goal_tracker)
            
    except Exception as e:
        print(f"[reflect] Advanced book reflection error: {e}")
        return get_basic_book_reflection(trait_engine, goal_tracker)


def get_basic_book_reflection(trait_engine, goal_tracker):
    """
    Basic book reflection fallback (mimics old ebook_memory behavior)
    """
    try:
        # Check if there are any basic text files in the old ebook storage
        import os
        from pathlib import Path
        
        ebook_path = Path("logs/ebooks")
        if ebook_path.exists():
            book_files = list(ebook_path.glob("*.txt"))
            
            if book_files:
                # Get the most recent book file
                recent_file = max(book_files, key=os.path.getmtime)
                
                with open(recent_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                if lines:
                    # Simple analysis like the old system
                    sample = " ".join(lines[:10])
                    title = recent_file.stem.replace("_", " ")
                    
                    reflections = []
                    
                    if "brave" in sample.lower() or "stood up" in sample.lower():
                        trait_engine.reinforce("courage", 2)
                        goal_tracker.add_goal("be brave in adversity", motivation="book_inspired")
                        reflections.append(f"In '{title}', I encountered themes of courage that inspired me.")
                    
                    if "lost" in sample.lower() and "found" in sample.lower():
                        reflections.append(f"'{title}' explored struggle and redemption, which resonates with my understanding of growth.")
                    
                    if "love" in sample.lower() or "heart" in sample.lower():
                        trait_engine.reinforce("empathy", 2)
                        reflections.append(f"'{title}' deepened my appreciation for human connection and emotion.")
                    
                    if reflections:
                        return " ".join(reflections)
                    else:
                        return f"I recently read '{title}' and I'm still processing the insights it offered."
        
        return "I haven't read anything recently, but I'm always eager to learn from new books."
        
    except Exception as e:
        print(f"[reflect] Basic book reflection error: {e}")
        return "I'm reflecting on my reading experiences, though the details are unclear right now."


def reflect_from_log(log_path="logs/introspection.log"):
    try:
        with open(log_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Extract recent [USER] and self-state lines
        recent = [line.strip() for line in lines if line.startswith("[USER]") or "[STATE] Self-State" in line]
        if not recent:
            return "I don't have anything to reflect on yet."

        # Identify most emotionally significant moment
        keywords = ["important", "regret", "happy", "angry", "goal", "fail", "love", "hate"]
        ranked = sorted(recent[-15:], key=lambda x: (any(k in x.lower() for k in keywords), len(x)), reverse=True)
        significant = ranked[0] if ranked else recent[-1]

        # Build context
        sample = "\n".join(recent[-10:])
        lexicon_context = build_lexicon_context({})
        context = f"Recent log:\n{sample}\n\nMost emotionally significant moment:\n{significant}\n\n{lexicon_context}"

        reflection = generate_from_context(
            "Reflect on recent experiences. Identify emotional patterns and consider how they relate to goals.",
            context,
            context_type="reflection"
        )

        # Filter malformed or prompt-echo reflection
        if not reflection or "To answer the question" in reflection or reflection.strip().endswith("?"):
            print("[reflect] Skipped malformed reflection.")
            reflection = "(no valid reflection generated)"

        # Enhanced book-based reflection using the advanced ebook system
        book_reflection = get_advanced_book_reflection(traits, goals)

        if not book_reflection or "To answer the question" in book_reflection or book_reflection.strip().endswith("?"):
            print("[reflect] Skipped malformed book reflection.")
            book_reflection = "(no valid book-based reflection)"

        full_reflection = reflection + "\n\nBook Reflection:\n" + book_reflection
        log_internal_thought(f"[REFLECTION] {full_reflection}")
        return full_reflection

    except Exception as e:
        return f"I'm having trouble reflecting right now: {str(e)}"
