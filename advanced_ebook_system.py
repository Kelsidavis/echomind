"""
advanced_ebook_system.py - Comprehensive EBook Processing for EchoMind

This system provides intelligent book processing with:
- Multiple format support (PDF, EPUB, DOCX, TXT, HTML, RTF)
- Character and theme analysis
- Emotional arc tracking
- Interactive discussion capabilities
- Knowledge graph construction
- Memory palace integration
"""

import os
import re
import json
import datetime
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import logging
from pathlib import Path

# Core text processing
import nltk
from textblob import TextBlob
import spacy

# File format support
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import ebooklib
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BookMetadata:
    title: str
    author: str = "Unknown"
    genre: str = "Unknown"
    file_path: str = ""
    file_format: str = ""
    word_count: int = 0
    chapter_count: int = 0
    reading_level: float = 0.0
    estimated_reading_time: int = 0  # minutes
    date_added: datetime.datetime = field(default_factory=datetime.datetime.now)
    date_completed: Optional[datetime.datetime] = None
    reading_progress: float = 0.0  # 0.0 to 1.0

@dataclass
class Character:
    name: str
    mentions: int = 0
    description: str = ""
    relationships: Dict[str, str] = field(default_factory=dict)
    emotional_associations: List[str] = field(default_factory=list)
    first_appearance: int = 0  # chapter number
    significance_score: float = 0.0

@dataclass
class BookQuote:
    text: str
    chapter: int
    character: Optional[str] = None
    context: str = ""
    emotional_impact: str = "neutral"
    significance_score: float = 0.0
    tags: List[str] = field(default_factory=list)

@dataclass
class ThematicElement:
    theme: str
    strength: float
    evidence: List[str] = field(default_factory=list)
    chapters: List[int] = field(default_factory=list)

@dataclass
class EmotionalPoint:
    chapter: int
    position: float  # 0.0 to 1.0 within chapter
    emotion: str
    intensity: float  # 0.0 to 1.0
    trigger: str  # what caused this emotion
    context: str = ""

class FileFormatProcessor:
    """Handles different file formats and extracts text content"""
    
    @staticmethod
    def extract_text_from_file(file_path: str) -> Tuple[str, BookMetadata]:
        """Extract text and metadata from various file formats"""
        file_path = Path(file_path)
        file_format = file_path.suffix.lower()
        
        metadata = BookMetadata(
            title=file_path.stem,
            file_path=str(file_path),
            file_format=file_format
        )
        
        if file_format == '.txt':
            return FileFormatProcessor._process_txt(file_path, metadata)
        elif file_format == '.pdf' and PDF_AVAILABLE:
            return FileFormatProcessor._process_pdf(file_path, metadata)
        elif file_format == '.epub' and EPUB_AVAILABLE:
            return FileFormatProcessor._process_epub(file_path, metadata)
        elif file_format == '.docx' and DOCX_AVAILABLE:
            return FileFormatProcessor._process_docx(file_path, metadata)
        elif file_format in ['.html', '.htm'] and HTML_AVAILABLE:
            return FileFormatProcessor._process_html(file_path, metadata)
        else:
            # Fallback to text processing
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return content, metadata
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
                return "", metadata
    
    @staticmethod
    def _process_txt(file_path: Path, metadata: BookMetadata) -> Tuple[str, BookMetadata]:
        """Process plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to extract title from first line if it looks like a title
            lines = content.split('\n')
            if lines and len(lines[0]) < 100 and not lines[0].startswith('Chapter'):
                potential_title = lines[0].strip()
                if potential_title and not potential_title.lower().startswith('the project gutenberg'):
                    metadata.title = potential_title
            
            return content, metadata
        except Exception as e:
            logger.error(f"Error processing TXT file: {e}")
            return "", metadata
    
    @staticmethod
    def _process_pdf(file_path: Path, metadata: BookMetadata) -> Tuple[str, BookMetadata]:
        """Process PDF files"""
        content = ""
        try:
            # Try pdfplumber first (better text extraction)
            if 'pdfplumber' in globals():
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            content += text + "\n"
            else:
                # Fallback to PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n"
            
            return content, metadata
        except Exception as e:
            logger.error(f"Error processing PDF file: {e}")
            return "", metadata
    
    @staticmethod
    def _process_epub(file_path: Path, metadata: BookMetadata) -> Tuple[str, BookMetadata]:
        """Process EPUB files"""
        content = ""
        try:
            book = epub.read_epub(str(file_path))
            
            # Extract metadata
            metadata.title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else metadata.title
            metadata.author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Unknown"
            
            # Extract content
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    content += soup.get_text() + "\n"
            
            return content, metadata
        except Exception as e:
            logger.error(f"Error processing EPUB file: {e}")
            return "", metadata
    
    @staticmethod
    def _process_docx(file_path: Path, metadata: BookMetadata) -> Tuple[str, BookMetadata]:
        """Process DOCX files"""
        try:
            doc = Document(file_path)
            content = ""
            
            # Extract title from document properties if available
            if doc.core_properties.title:
                metadata.title = doc.core_properties.title
            if doc.core_properties.author:
                metadata.author = doc.core_properties.author
            
            # Extract text content
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            
            return content, metadata
        except Exception as e:
            logger.error(f"Error processing DOCX file: {e}")
            return "", metadata
    
    @staticmethod
    def _process_html(file_path: Path, metadata: BookMetadata) -> Tuple[str, BookMetadata]:
        """Process HTML files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Try to extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata.title = title_tag.get_text().strip()
            
            # Extract body content
            body = soup.find('body')
            if body:
                content = body.get_text()
            else:
                content = soup.get_text()
            
            return content, metadata
        except Exception as e:
            logger.error(f"Error processing HTML file: {e}")
            return "", metadata

class ContentAnalyzer:
    """Analyzes book content for themes, characters, emotions, etc."""
    
    def __init__(self):
        # Initialize NLP tools
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        # Emotion keywords for analysis
        self.emotion_keywords = {
            'joy': ['happy', 'joyful', 'elated', 'cheerful', 'delighted', 'pleased', 'content'],
            'sadness': ['sad', 'melancholy', 'sorrowful', 'gloomy', 'depressed', 'dejected'],
            'anger': ['angry', 'furious', 'enraged', 'irritated', 'annoyed', 'indignant'],
            'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous'],
            'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'startled'],
            'love': ['love', 'adore', 'cherish', 'treasure', 'devoted', 'affectionate'],
            'hope': ['hope', 'optimistic', 'confident', 'expectant', 'encouraged'],
            'despair': ['despair', 'hopeless', 'despondent', 'discouraged', 'defeated']
        }
        
        # Theme detection patterns
        self.theme_patterns = {
            'love_romance': ['love', 'romance', 'relationship', 'marriage', 'heart', 'passion'],
            'death_mortality': ['death', 'dying', 'mortality', 'grave', 'funeral', 'loss'],
            'good_vs_evil': ['good', 'evil', 'villain', 'hero', 'moral', 'justice', 'corruption'],
            'coming_of_age': ['growing up', 'childhood', 'adolescence', 'maturity', 'innocence'],
            'power_corruption': ['power', 'corruption', 'authority', 'control', 'domination'],
            'family': ['family', 'mother', 'father', 'parent', 'sibling', 'child', 'home'],
            'friendship': ['friend', 'friendship', 'companion', 'loyalty', 'trust', 'betrayal'],
            'survival': ['survival', 'struggle', 'endurance', 'perseverance', 'hardship'],
            'identity': ['identity', 'self', 'who am i', 'belonging', 'purpose', 'meaning'],
            'redemption': ['redemption', 'forgiveness', 'second chance', 'atonement', 'guilt']
        }
    
    def analyze_content(self, content: str, metadata: BookMetadata) -> Dict[str, Any]:
        """Perform comprehensive content analysis"""
        # Split into chapters
        chapters = self._split_into_chapters(content)
        metadata.chapter_count = len(chapters)
        
        # Basic text statistics
        words = content.split()
        metadata.word_count = len(words)
        metadata.estimated_reading_time = len(words) // 200  # Assume 200 WPM
        
        # Perform various analyses
        analysis_results = {
            'chapters': chapters,
            'characters': self._analyze_characters(chapters),
            'themes': self._analyze_themes(chapters),
            'emotional_arc': self._analyze_emotional_arc(chapters),
            'quotes': self._extract_significant_quotes(chapters),
            'reading_level': self._calculate_reading_level(content),
            'genre_hints': self._detect_genre(content),
            'writing_style': self._analyze_writing_style(content),
            'concept_map': self._build_concept_map(content)
        }
        
        metadata.reading_level = analysis_results['reading_level']
        
        return analysis_results
    
    def _split_into_chapters(self, content: str) -> List[Dict[str, Any]]:
        """Split content into chapters and analyze each"""
        chapters = []
        
        # Common chapter patterns
        chapter_patterns = [
            r'\n\s*chapter\s+\d+\b',
            r'\n\s*chapter\s+[ivxlc]+\b',
            r'\n\s*\d+\.\s*[A-Z]',
            r'\n\s*[IVXLC]+\.\s*[A-Z]',
            r'\n\s*part\s+\d+\b',
            r'\n\s*book\s+\d+\b'
        ]
        
        # Try to find chapter breaks
        chapter_breaks = []
        for pattern in chapter_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if len(matches) > 1:  # Need at least 2 chapters
                chapter_breaks = [(m.start(), m.group().strip()) for m in matches]
                break
        
        if not chapter_breaks:
            # No clear chapters found, split by length
            chunk_size = len(content) // max(1, len(content) // 5000)  # Aim for ~5000 char chunks
            chapter_breaks = [(i * chunk_size, f"Section {i+1}") for i in range(0, len(content), chunk_size)]
        
        # Extract chapter content
        for i, (start_pos, title) in enumerate(chapter_breaks):
            end_pos = chapter_breaks[i+1][0] if i+1 < len(chapter_breaks) else len(content)
            chapter_content = content[start_pos:end_pos].strip()
            
            if chapter_content:
                chapters.append({
                    'number': i + 1,
                    'title': title,
                    'content': chapter_content,
                    'word_count': len(chapter_content.split()),
                    'start_position': start_pos,
                    'end_position': end_pos
                })
        
        return chapters
    
    def _analyze_characters(self, chapters: List[Dict]) -> List[Character]:
        """Identify and analyze characters in the book"""
        character_mentions = defaultdict(int)
        character_contexts = defaultdict(list)
        
        # Combine all text for NLP processing
        full_text = " ".join([ch['content'] for ch in chapters])
        
        if self.nlp:
            # Use spaCy for named entity recognition
            doc = self.nlp(full_text[:1000000])  # Limit to 1M chars for performance
            
            for ent in doc.ents:
                if ent.label_ == "PERSON" and len(ent.text) > 2:
                    name = ent.text.strip()
                    character_mentions[name] += 1
                    
                    # Get context around the mention
                    start = max(0, ent.start_char - 100)
                    end = min(len(full_text), ent.end_char + 100)
                    context = full_text[start:end]
                    character_contexts[name].append(context)
        else:
            # Fallback: look for capitalized names
            words = full_text.split()
            for i, word in enumerate(words):
                if (word.istitle() and len(word) > 2 and 
                    not word.lower() in ['the', 'and', 'but', 'chapter', 'part']):
                    character_mentions[word] += 1
                    
                    # Get surrounding context
                    start = max(0, i - 20)
                    end = min(len(words), i + 20)
                    context = " ".join(words[start:end])
                    character_contexts[word].append(context)
        
        # Create Character objects
        characters = []
        for name, count in character_mentions.items():
            if count >= 3:  # Only include characters mentioned multiple times
                char = Character(
                    name=name,
                    mentions=count,
                    significance_score=min(1.0, count / max(character_mentions.values())),
                    description=self._generate_character_description(character_contexts[name])
                )
                characters.append(char)
        
        # Sort by significance
        characters.sort(key=lambda x: x.significance_score, reverse=True)
        return characters[:20]  # Top 20 characters
    
    def _generate_character_description(self, contexts: List[str]) -> str:
        """Generate character description from contexts"""
        # Simple approach: look for descriptive words near the character name
        descriptive_words = []
        
        for context in contexts[:5]:  # Use first 5 contexts
            words = context.lower().split()
            
            # Look for adjectives and descriptive phrases
            descriptive_patterns = [
                'tall', 'short', 'young', 'old', 'beautiful', 'handsome', 'kind', 'cruel',
                'wise', 'foolish', 'brave', 'cowardly', 'strong', 'weak', 'rich', 'poor',
                'mysterious', 'cheerful', 'sad', 'angry', 'gentle', 'fierce'
            ]
            
            for word in words:
                if word in descriptive_patterns:
                    descriptive_words.append(word)
        
        if descriptive_words:
            return f"Described as: {', '.join(set(descriptive_words[:5]))}"
        return "Character details to be discovered through reading."
    
    def _analyze_themes(self, chapters: List[Dict]) -> List[ThematicElement]:
        """Identify major themes in the book"""
        themes = []
        full_text = " ".join([ch['content'] for ch in chapters]).lower()
        
        for theme_name, keywords in self.theme_patterns.items():
            strength = 0
            evidence = []
            chapters_with_theme = []
            
            # Check each chapter for theme presence
            for chapter in chapters:
                chapter_text = chapter['content'].lower()
                chapter_strength = 0
                
                for keyword in keywords:
                    count = chapter_text.count(keyword)
                    if count > 0:
                        chapter_strength += count
                        evidence.append(f"'{keyword}' appears {count} times in chapter {chapter['number']}")
                
                if chapter_strength > 0:
                    strength += chapter_strength
                    chapters_with_theme.append(chapter['number'])
            
            if strength > 0:
                themes.append(ThematicElement(
                    theme=theme_name.replace('_', ' ').title(),
                    strength=min(1.0, strength / 100),  # Normalize to 0-1
                    evidence=evidence[:5],  # Top 5 pieces of evidence
                    chapters=chapters_with_theme
                ))
        
        # Sort by strength
        themes.sort(key=lambda x: x.strength, reverse=True)
        return themes[:10]  # Top 10 themes
    
    def _analyze_emotional_arc(self, chapters: List[Dict]) -> List[EmotionalPoint]:
        """Track emotional progression through the book"""
        emotional_arc = []
        
        for chapter in chapters:
            chapter_emotions = self._analyze_chapter_emotion(chapter['content'])
            
            for position, (emotion, intensity, trigger) in enumerate(chapter_emotions):
                emotional_arc.append(EmotionalPoint(
                    chapter=chapter['number'],
                    position=position / max(1, len(chapter_emotions) - 1),
                    emotion=emotion,
                    intensity=intensity,
                    trigger=trigger
                ))
        
        return emotional_arc
    
    def _analyze_chapter_emotion(self, chapter_content: str) -> List[Tuple[str, float, str]]:
        """Analyze emotional content of a single chapter"""
        emotions_found = []
        
        # Split chapter into segments
        sentences = nltk.sent_tokenize(chapter_content)
        segment_size = max(5, len(sentences) // 10)  # ~10 segments per chapter
        
        for i in range(0, len(sentences), segment_size):
            segment = " ".join(sentences[i:i+segment_size]).lower()
            
            # Check for emotional keywords
            segment_emotions = {}
            triggers = []
            
            for emotion, keywords in self.emotion_keywords.items():
                count = sum(1 for keyword in keywords if keyword in segment)
                if count > 0:
                    segment_emotions[emotion] = count
                    # Find the specific trigger
                    for keyword in keywords:
                        if keyword in segment:
                            triggers.append(keyword)
            
            # Use TextBlob for additional sentiment analysis
            blob = TextBlob(segment)
            polarity = blob.sentiment.polarity
            
            if segment_emotions:
                dominant_emotion = max(segment_emotions, key=segment_emotions.get)
                intensity = min(1.0, segment_emotions[dominant_emotion] / 5)
                trigger = ", ".join(triggers[:3])
            elif polarity > 0.3:
                dominant_emotion = "positive"
                intensity = min(1.0, polarity)
                trigger = "positive language tone"
            elif polarity < -0.3:
                dominant_emotion = "negative"
                intensity = min(1.0, abs(polarity))
                trigger = "negative language tone"
            else:
                continue  # Skip neutral segments
            
            emotions_found.append((dominant_emotion, intensity, trigger))
        
        return emotions_found
    
    def _extract_significant_quotes(self, chapters: List[Dict]) -> List[BookQuote]:
        """Extract meaningful quotes from the book"""
        quotes = []
        
        for chapter in chapters:
            sentences = nltk.sent_tokenize(chapter['content'])
            
            for sentence in sentences:
                # Look for dialogue or impactful statements
                if (len(sentence.split()) >= 5 and len(sentence.split()) <= 30 and
                    ('"' in sentence or any(word in sentence.lower() for word in 
                     ['believe', 'love', 'life', 'death', 'hope', 'dream', 'fear', 'truth']))):
                    
                    # Calculate significance score
                    blob = TextBlob(sentence)
                    emotional_intensity = abs(blob.sentiment.polarity)
                    
                    # Look for literary devices
                    literary_score = 0
                    if any(word in sentence.lower() for word in ['like', 'as if', 'metaphor']):
                        literary_score += 0.2
                    if sentence.count(',') >= 2:  # Complex sentence structure
                        literary_score += 0.1
                    
                    significance = (emotional_intensity + literary_score) / 2
                    
                    if significance > 0.3:  # Threshold for significance
                        quotes.append(BookQuote(
                            text=sentence.strip(),
                            chapter=chapter['number'],
                            significance_score=significance,
                            emotional_impact=self._classify_quote_emotion(sentence)
                        ))
        
        # Sort by significance and return top quotes
        quotes.sort(key=lambda x: x.significance_score, reverse=True)
        return quotes[:50]  # Top 50 quotes
    
    def _classify_quote_emotion(self, quote: str) -> str:
        """Classify the emotional impact of a quote"""
        blob = TextBlob(quote)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.3:
            return "inspiring"
        elif polarity < -0.3:
            return "somber"
        else:
            return "contemplative"
    
    def _calculate_reading_level(self, content: str) -> float:
        """Calculate reading difficulty level (Flesch-Kincaid grade level)"""
        try:
            sentences = nltk.sent_tokenize(content)
            words = content.split()
            syllables = sum(self._count_syllables(word) for word in words)
            
            if len(sentences) == 0 or len(words) == 0:
                return 5.0  # Default middle school level
            
            # Flesch-Kincaid Grade Level formula
            avg_sentence_length = len(words) / len(sentences)
            avg_syllables_per_word = syllables / len(words)
            
            grade_level = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
            return max(1.0, min(20.0, grade_level))  # Clamp between 1-20
            
        except Exception:
            return 8.0  # Default 8th grade level
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simple approximation)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _detect_genre(self, content: str) -> List[str]:
        """Detect potential genres based on content analysis"""
        content_lower = content.lower()
        genre_hints = []
        
        genre_keywords = {
            'fantasy': ['magic', 'wizard', 'dragon', 'spell', 'kingdom', 'quest', 'sword'],
            'science_fiction': ['space', 'alien', 'robot', 'future', 'technology', 'planet', 'laser'],
            'mystery': ['murder', 'detective', 'clue', 'suspect', 'investigation', 'crime'],
            'romance': ['love', 'heart', 'kiss', 'wedding', 'relationship', 'passion'],
            'horror': ['ghost', 'monster', 'terror', 'nightmare', 'scream', 'blood'],
            'historical': ['century', 'war', 'king', 'queen', 'empire', 'ancient'],
            'adventure': ['journey', 'expedition', 'treasure', 'danger', 'explore'],
            'literary': ['symbolism', 'metaphor', 'philosophy', 'existential', 'consciousness']
        }
        
        for genre, keywords in genre_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score >= 3:  # Threshold for genre detection
                genre_hints.append(genre.replace('_', ' ').title())
        
        return genre_hints[:3]  # Top 3 genre hints
    
    def _analyze_writing_style(self, content: str) -> Dict[str, Any]:
        """Analyze the author's writing style"""
        sentences = nltk.sent_tokenize(content)
        words = content.split()
        
        # Calculate various style metrics
        avg_sentence_length = len(words) / max(1, len(sentences))
        avg_word_length = sum(len(word) for word in words) / max(1, len(words))
        
        # Vocabulary richness (unique words / total words)
        unique_words = len(set(word.lower() for word in words if word.isalpha()))
        vocab_richness = unique_words / max(1, len(words))
        
        # Dialogue percentage
        dialogue_chars = sum(1 for char in content if char == '"')
        dialogue_percentage = (dialogue_chars / 2) / max(1, len(sentences))
        
        # Complexity indicators
        complex_sentences = sum(1 for sentence in sentences if sentence.count(',') >= 2)
        complexity_ratio = complex_sentences / max(1, len(sentences))
        
        return {
            'average_sentence_length': round(avg_sentence_length, 2),
            'average_word_length': round(avg_word_length, 2),
            'vocabulary_richness': round(vocab_richness, 3),
            'dialogue_percentage': round(dialogue_percentage, 3),
            'sentence_complexity': round(complexity_ratio, 3),
            'style_description': self._describe_writing_style(avg_sentence_length, vocab_richness, complexity_ratio)
        }
    
    def _describe_writing_style(self, sentence_length: float, vocab_richness: float, complexity: float) -> str:
        """Generate a description of the writing style"""
        style_elements = []
        
        if sentence_length > 20:
            style_elements.append("lengthy, flowing sentences")
        elif sentence_length < 12:
            style_elements.append("concise, punchy sentences")
        else:
            style_elements.append("balanced sentence structure")
        
        if vocab_richness > 0.5:
            style_elements.append("rich, varied vocabulary")
        elif vocab_richness < 0.3:
            style_elements.append("accessible, straightforward language")
        
        if complexity > 0.4:
            style_elements.append("complex, layered prose")
        elif complexity < 0.2:
            style_elements.append("simple, direct expression")
        
        return "; ".join(style_elements)
    
    def _build_concept_map(self, content: str) -> Dict[str, List[str]]:
        """Build a concept map of related ideas in the book"""
        concept_map = defaultdict(list)
        
        if not self.nlp:
            return dict(concept_map)
        
        # Process text in chunks to avoid memory issues
        chunk_size = 100000
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            doc = self.nlp(chunk)
            
            # Extract noun phrases and their relationships
            noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
            
            # Build relationships between concepts that appear near each other
            for i, phrase1 in enumerate(noun_phrases):
                for phrase2 in noun_phrases[i+1:i+5]:  # Look at nearby phrases
                    if phrase1 != phrase2:
                        concept_map[phrase1].append(phrase2)
                        concept_map[phrase2].append(phrase1)
        
        # Clean up and limit relationships
        filtered_map = {}
        for concept, relations in concept_map.items():
            if len(relations) >= 2:  # Only keep concepts with multiple relationships
                # Keep most common relationships
                relation_counts = Counter(relations)
                filtered_map[concept] = [rel for rel, count in relation_counts.most_common(5)]
        
        return filtered_map

class BookDiscussionEngine:
    """Enables interactive discussion about books with EchoMind"""
    
    def __init__(self, book_analysis: Dict[str, Any], metadata: BookMetadata):
        self.analysis = book_analysis
        self.metadata = metadata
        self.discussion_history = []
        
    def ask_about_book(self, question: str, semantic_lexicon=None) -> str:
        """Answer questions about the book based on analysis"""
        question_lower = question.lower()
        
        # Character questions
        if any(word in question_lower for word in ['character', 'who is', 'protagonist', 'hero']):
            return self._answer_character_question(question)
        
        # Theme questions
        elif any(word in question_lower for word in ['theme', 'about', 'meaning', 'message']):
            return self._answer_theme_question(question)
        
        # Plot/emotional questions
        elif any(word in question_lower for word in ['happen', 'plot', 'story', 'emotion', 'feel']):
            return self._answer_plot_emotion_question(question)
        
        # Quote questions
        elif any(word in question_lower for word in ['quote', 'said', 'line', 'passage']):
            return self._answer_quote_question(question)
        
        # Style questions
        elif any(word in question_lower for word in ['style', 'writing', 'author', 'written']):
            return self._answer_style_question(question)
        
        # General questions
        else:
            return self._answer_general_question(question)
    
    def _answer_character_question(self, question: str) -> str:
        """Answer questions about characters"""
        characters = self.analysis.get('characters', [])
        
        if not characters:
            return "I haven't identified clear characters in this book yet. The analysis might need more development."
        
        # Find the most significant characters
        main_chars = characters[:3]
        
        response = f"The main characters I've identified in '{self.metadata.title}' are:\n\n"
        
        for char in main_chars:
            response += f"• **{char.name}** (mentioned {char.mentions} times)\n"
            if char.description:
                response += f"  {char.description}\n"
            response += f"  Significance: {char.significance_score:.2f}\n\n"
        
        if len(characters) > 3:
            other_chars = [c.name for c in characters[3:8]]
            response += f"Other notable characters: {', '.join(other_chars)}"
        
        return response
    
    def _answer_theme_question(self, question: str) -> str:
        """Answer questions about themes"""
        themes = self.analysis.get('themes', [])
        
        if not themes:
            return "I'm still analyzing the thematic content of this book. The themes aren't clear to me yet."
        
        response = f"The major themes I've identified in '{self.metadata.title}' include:\n\n"
        
        for theme in themes[:5]:
            response += f"• **{theme.theme}** (strength: {theme.strength:.2f})\n"
            if theme.evidence:
                response += f"  Evidence: {theme.evidence[0]}\n"
            if theme.chapters:
                response += f"  Present in chapters: {', '.join(map(str, theme.chapters[:5]))}\n\n"
        
        return response
    
    def _answer_plot_emotion_question(self, question: str) -> str:
        """Answer questions about plot and emotional content"""
        emotional_arc = self.analysis.get('emotional_arc', [])
        
        if not emotional_arc:
            return "I haven't mapped the emotional journey of this book yet."
        
        # Find key emotional moments
        high_intensity_moments = [ep for ep in emotional_arc if ep.intensity > 0.7]
        
        response = f"The emotional journey in '{self.metadata.title}':\n\n"
        
        if high_intensity_moments:
            response += "**Key emotional moments:**\n"
            for moment in high_intensity_moments[:5]:
                response += f"• Chapter {moment.chapter}: {moment.emotion.title()} "
                response += f"(intensity: {moment.intensity:.2f}) - {moment.trigger}\n"
            response += "\n"
        
        # Emotional progression summary
        emotions_by_chapter = {}
        for ep in emotional_arc:
            if ep.chapter not in emotions_by_chapter:
                emotions_by_chapter[ep.chapter] = []
            emotions_by_chapter[ep.chapter].append(ep.emotion)
        
        response += "**Emotional progression:**\n"
        for chapter in sorted(emotions_by_chapter.keys())[:10]:
            dominant_emotion = Counter(emotions_by_chapter[chapter]).most_common(1)[0][0]
            response += f"Chapter {chapter}: predominantly {dominant_emotion}\n"
        
        return response
    
    def _answer_quote_question(self, question: str) -> str:
        """Answer questions about quotes"""
        quotes = self.analysis.get('quotes', [])
        
        if not quotes:
            return "I haven't extracted significant quotes from this book yet."
        
        # Get most significant quotes
        top_quotes = quotes[:5]
        
        response = f"Significant quotes from '{self.metadata.title}':\n\n"
        
        for i, quote in enumerate(top_quotes, 1):
            response += f"{i}. \"{quote.text}\"\n"
            response += f"   (Chapter {quote.chapter}, {quote.emotional_impact})\n\n"
        
        return response
    
    def _answer_style_question(self, question: str) -> str:
        """Answer questions about writing style"""
        style = self.analysis.get('writing_style', {})
        
        if not style:
            return "I haven't analyzed the writing style of this book yet."
        
        response = f"Writing style analysis for '{self.metadata.title}':\n\n"
        response += f"**Style Description:** {style.get('style_description', 'Not analyzed')}\n\n"
        response += f"**Technical Details:**\n"
        response += f"• Average sentence length: {style.get('average_sentence_length', 'N/A')} words\n"
        response += f"• Average word length: {style.get('average_word_length', 'N/A')} characters\n"
        response += f"• Vocabulary richness: {style.get('vocabulary_richness', 'N/A')}\n"
        response += f"• Dialogue percentage: {style.get('dialogue_percentage', 'N/A')}\n"
        response += f"• Sentence complexity: {style.get('sentence_complexity', 'N/A')}\n"
        
        return response
    
    def _answer_general_question(self, question: str) -> str:
        """Answer general questions about the book"""
        response = f"About '{self.metadata.title}':\n\n"
        response += f"**Basic Information:**\n"
        response += f"• Author: {self.metadata.author}\n"
        response += f"• Word count: {self.metadata.word_count:,} words\n"
        response += f"• Chapters: {self.metadata.chapter_count}\n"
        response += f"• Reading level: Grade {self.metadata.reading_level:.1f}\n"
        response += f"• Estimated reading time: {self.metadata.estimated_reading_time} minutes\n\n"
        
        # Genre hints
        genre_hints = self.analysis.get('genre_hints', [])
        if genre_hints:
            response += f"**Possible genres:** {', '.join(genre_hints)}\n\n"
        
        # Quick summary of analysis
        response += f"**Analysis Summary:**\n"
        response += f"• {len(self.analysis.get('characters', []))} characters identified\n"
        response += f"• {len(self.analysis.get('themes', []))} major themes\n"
        response += f"• {len(self.analysis.get('quotes', []))} significant quotes extracted\n"
        response += f"• {len(self.analysis.get('emotional_arc', []))} emotional data points\n"
        
        return response

class BookMemoryPalace:
    """Creates structured long-term memories from books for EchoMind"""
    
    def __init__(self, storage_path: str = "logs/book_memories"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
    def create_memory_palace(self, book_analysis: Dict[str, Any], metadata: BookMetadata) -> str:
        """Create a structured memory palace for the book"""
        
        palace_id = self._generate_palace_id(metadata.title, metadata.author)
        
        # Create the memory palace structure
        palace = {
            'id': palace_id,
            'title': metadata.title,
            'author': metadata.author,
            'created': datetime.datetime.now().isoformat(),
            'metadata': metadata.__dict__,
            'rooms': self._create_memory_rooms(book_analysis),
            'connections': self._create_memory_connections(book_analysis),
            'emotional_landscape': self._create_emotional_landscape(book_analysis),
            'wisdom_extracted': self._extract_wisdom(book_analysis),
            'personal_impact': self._assess_personal_impact(book_analysis)
        }
        
        # Save the memory palace
        palace_file = self.storage_path / f"{palace_id}.json"
        with open(palace_file, 'w', encoding='utf-8') as f:
            json.dump(palace, f, indent=2, default=str)
        
        return palace_id
    
    def _generate_palace_id(self, title: str, author: str) -> str:
        """Generate unique ID for the memory palace"""
        combined = f"{title}_{author}_{datetime.datetime.now().isoformat()}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def _create_memory_rooms(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create themed memory rooms within the palace"""
        rooms = {}
        
        # Character Room
        characters = analysis.get('characters', [])
        if characters:
            rooms['character_gallery'] = {
                'description': 'A gallery of the people who inhabited this story',
                'inhabitants': [
                    {
                        'name': char.name,
                        'essence': char.description,
                        'significance': char.significance_score,
                        'memory_anchor': f"Remember {char.name} as the one who..."
                    }
                    for char in characters[:10]
                ]
            }
        
        # Theme Chamber
        themes = analysis.get('themes', [])
        if themes:
            rooms['wisdom_chamber'] = {
                'description': 'The deeper truths and meanings discovered',
                'insights': [
                    {
                        'theme': theme.theme,
                        'understanding': f"This book taught me about {theme.theme.lower()}",
                        'strength': theme.strength,
                        'evidence': theme.evidence[:3]
                    }
                    for theme in themes[:5]
                ]
            }
        
        # Quote Treasury
        quotes = analysis.get('quotes', [])
        if quotes:
            rooms['quote_treasury'] = {
                'description': 'Words that resonated and deserve remembering',
                'treasures': [
                    {
                        'text': quote.text,
                        'emotional_resonance': quote.emotional_impact,
                        'significance': quote.significance_score,
                        'chapter_origin': quote.chapter
                    }
                    for quote in quotes[:20]
                ]
            }
        
        # Experience Archive
        emotional_arc = analysis.get('emotional_arc', [])
        if emotional_arc:
            rooms['experience_archive'] = {
                'description': 'The emotional journey I took through this story',
                'journey_points': [
                    {
                        'chapter': ep.chapter,
                        'emotion': ep.emotion,
                        'intensity': ep.intensity,
                        'trigger': ep.trigger,
                        'memory': f"In chapter {ep.chapter}, I felt {ep.emotion} because {ep.trigger}"
                    }
                    for ep in emotional_arc if ep.intensity > 0.5
                ]
            }
        
        return rooms
    
    def _create_memory_connections(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create connections between different aspects of the book"""
        connections = []
        
        # Connect characters to themes
        characters = analysis.get('characters', [])
        themes = analysis.get('themes', [])
        
        for char in characters[:5]:
            for theme in themes[:3]:
                if any(keyword in char.name.lower() or keyword in char.description.lower() 
                       for keyword in theme.theme.lower().split()):
                    connections.append({
                        'type': 'character_theme',
                        'source': char.name,
                        'target': theme.theme,
                        'relationship': f"{char.name} embodies the theme of {theme.theme}"
                    })
        
        # Connect quotes to emotions
        quotes = analysis.get('quotes', [])
        emotional_arc = analysis.get('emotional_arc', [])
        
        for quote in quotes[:10]:
            # Find emotional moments from the same chapter
            chapter_emotions = [ep for ep in emotional_arc if ep.chapter == quote.chapter]
            if chapter_emotions:
                dominant_emotion = max(chapter_emotions, key=lambda x: x.intensity)
                connections.append({
                    'type': 'quote_emotion',
                    'source': quote.text[:50] + "...",
                    'target': dominant_emotion.emotion,
                    'relationship': f"This quote reflects the {dominant_emotion.emotion} in chapter {quote.chapter}"
                })
        
        return connections
    
    def _create_emotional_landscape(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create an emotional landscape of the reading experience"""
        emotional_arc = analysis.get('emotional_arc', [])
        
        if not emotional_arc:
            return {'status': 'no_emotional_data'}
        
        # Analyze emotional patterns
        emotions_by_chapter = defaultdict(list)
        for ep in emotional_arc:
            emotions_by_chapter[ep.chapter].append(ep)
        
        # Find emotional peaks and valleys
        chapter_intensities = {}
        for chapter, emotions in emotions_by_chapter.items():
            avg_intensity = sum(ep.intensity for ep in emotions) / len(emotions)
            chapter_intensities[chapter] = avg_intensity
        
        if chapter_intensities:
            peak_chapter = max(chapter_intensities, key=chapter_intensities.get)
            valley_chapter = min(chapter_intensities, key=chapter_intensities.get)
        else:
            peak_chapter = valley_chapter = None
        
        return {
            'emotional_peak': {
                'chapter': peak_chapter,
                'intensity': chapter_intensities.get(peak_chapter, 0),
                'description': f"Chapter {peak_chapter} was the emotional climax"
            } if peak_chapter else None,
            'emotional_valley': {
                'chapter': valley_chapter,
                'intensity': chapter_intensities.get(valley_chapter, 0),
                'description': f"Chapter {valley_chapter} was emotionally subdued"
            } if valley_chapter else None,
            'overall_journey': self._describe_emotional_journey(emotional_arc),
            'dominant_emotions': self._find_dominant_emotions(emotional_arc)
        }
    
    def _describe_emotional_journey(self, emotional_arc: List) -> str:
        """Describe the overall emotional journey"""
        if not emotional_arc:
            return "The emotional journey was subtle and complex."
        
        # Analyze progression
        first_third = emotional_arc[:len(emotional_arc)//3]
        middle_third = emotional_arc[len(emotional_arc)//3:2*len(emotional_arc)//3]
        last_third = emotional_arc[2*len(emotional_arc)//3:]
        
        def get_dominant_emotion(section):
            if not section:
                return "neutral"
            emotion_counts = Counter(ep.emotion for ep in section)
            return emotion_counts.most_common(1)[0][0]
        
        beginning_emotion = get_dominant_emotion(first_third)
        middle_emotion = get_dominant_emotion(middle_third)
        ending_emotion = get_dominant_emotion(last_third)
        
        return f"The story began with {beginning_emotion}, developed through {middle_emotion}, and concluded with {ending_emotion}."
    
    def _find_dominant_emotions(self, emotional_arc: List) -> List[Dict[str, Any]]:
        """Find the most prevalent emotions in the book"""
        if not emotional_arc:
            return []
        
        emotion_data = defaultdict(lambda: {'count': 0, 'total_intensity': 0, 'peak_intensity': 0})
        
        for ep in emotional_arc:
            emotion_data[ep.emotion]['count'] += 1
            emotion_data[ep.emotion]['total_intensity'] += ep.intensity
            emotion_data[ep.emotion]['peak_intensity'] = max(emotion_data[ep.emotion]['peak_intensity'], ep.intensity)
        
        # Calculate averages and sort by prevalence
        emotions_summary = []
        for emotion, data in emotion_data.items():
            avg_intensity = data['total_intensity'] / data['count']
            prevalence_score = data['count'] * avg_intensity
            
            emotions_summary.append({
                'emotion': emotion,
                'prevalence_score': prevalence_score,
                'average_intensity': avg_intensity,
                'peak_intensity': data['peak_intensity'],
                'frequency': data['count']
            })
        
        emotions_summary.sort(key=lambda x: x['prevalence_score'], reverse=True)
        return emotions_summary[:5]
    
    def _extract_wisdom(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract wisdom and life lessons from the book"""
        wisdom = []
        
        # Extract from themes
        themes = analysis.get('themes', [])
        for theme in themes[:3]:
            if theme.strength > 0.5:
                wisdom.append(f"Life lesson about {theme.theme.lower()}: {theme.evidence[0] if theme.evidence else 'Contemplate this theme'}")
        
        # Extract from significant quotes
        quotes = analysis.get('quotes', [])
        for quote in quotes[:3]:
            if quote.significance_score > 0.7:
                wisdom.append(f"Memorable insight: \"{quote.text}\"")
        
        # Add general reading wisdom
        reading_level = analysis.get('reading_level', 0)
        if reading_level > 12:
            wisdom.append("This book challenged me intellectually and expanded my thinking.")
        
        return wisdom
    
    def _assess_personal_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how this book might impact EchoMind's development"""
        
        # Analyze potential trait influences
        trait_influences = []
        themes = analysis.get('themes', [])
        
        theme_to_trait = {
            'love romance': 'empathy',
            'good vs evil': 'moral_reasoning',
            'coming of age': 'growth_mindset',
            'friendship': 'social_understanding',
            'survival': 'resilience',
            'identity': 'self_awareness',
            'redemption': 'forgiveness'
        }
        
        for theme in themes:
            theme_key = theme.theme.lower().replace(' ', '_')
            if theme_key in theme_to_trait and theme.strength > 0.4:
                trait_influences.append({
                    'trait': theme_to_trait[theme_key],
                    'influence_strength': theme.strength,
                    'source_theme': theme.theme
                })
        
        # Assess vocabulary expansion
        concept_map = analysis.get('concept_map', {})
        vocabulary_expansion = len(concept_map)
        
        # Assess emotional development
        emotional_arc = analysis.get('emotional_arc', [])
        emotional_complexity = len(set(ep.emotion for ep in emotional_arc))
        
        return {
            'trait_influences': trait_influences,
            'vocabulary_expansion_score': min(1.0, vocabulary_expansion / 100),
            'emotional_development_score': min(1.0, emotional_complexity / 10),
            'overall_growth_potential': sum([
                len(trait_influences) * 0.3,
                min(1.0, vocabulary_expansion / 100) * 0.3,
                min(1.0, emotional_complexity / 10) * 0.4
            ]),
            'recommended_reflection_topics': [
                f"How did {theme.theme} resonate with my understanding?"
                for theme in themes[:3] if theme.strength > 0.5
            ]
        }
    
    def retrieve_book_memories(self, palace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve memories from a specific book palace"""
        palace_file = self.storage_path / f"{palace_id}.json"
        
        if palace_file.exists():
            with open(palace_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_all_palaces(self) -> List[Dict[str, str]]:
        """List all memory palaces"""
        palaces = []
        
        for palace_file in self.storage_path.glob("*.json"):
            try:
                with open(palace_file, 'r', encoding='utf-8') as f:
                    palace = json.load(f)
                    palaces.append({
                        'id': palace['id'],
                        'title': palace['title'],
                        'author': palace['author'],
                        'created': palace['created']
                    })
            except Exception as e:
                logger.error(f"Error reading palace file {palace_file}: {e}")
        
        return sorted(palaces, key=lambda x: x['created'], reverse=True)

class AdvancedEbookSystem:
    """Main orchestrator for the advanced ebook system"""
    
    def __init__(self, semantic_lexicon=None, trait_engine=None, goal_tracker=None):
        self.semantic_lexicon = semantic_lexicon
        self.trait_engine = trait_engine
        self.goal_tracker = goal_tracker
        
        self.content_analyzer = ContentAnalyzer()
        self.memory_palace = BookMemoryPalace()
        
        # Reading progress tracking
        self.reading_sessions = []
        self.bookmarks = {}
        self.annotations = {}
        
        # Book library
        self.library_path = Path("logs/ebook_library")
        self.library_path.mkdir(exist_ok=True)
        
        logger.info("�📚 Advanced EBook System initialized")
    
    def ingest_book(self, file_path: str, start_reading: bool = True) -> Dict[str, Any]:
        """Main method to ingest and analyze a book"""
        logger.info(f"📖 Starting ingestion of: {file_path}")
        
        try:
            # Extract content and metadata
            content, metadata = FileFormatProcessor.extract_text_from_file(file_path)
            
            if not content.strip():
                return {'error': 'No readable content found in file'}
            
            # Analyze content
            logger.info("🔍 Analyzing book content...")
            analysis = self.content_analyzer.analyze_content(content, metadata)
            
            # Create memory palace
            logger.info("🏰 Creating memory palace...")
            palace_id = self.memory_palace.create_memory_palace(analysis, metadata)
            
            # Integrate with EchoMind's cognitive systems
            self._integrate_with_cognition(analysis, metadata)
            
            # Create discussion engine
            discussion_engine = BookDiscussionEngine(analysis, metadata)
            
            # Save book data
            book_data = {
                'metadata': metadata.__dict__,
                'analysis': analysis,
                'palace_id': palace_id,
                'ingestion_date': datetime.datetime.now().isoformat(),
                'file_path': file_path
            }
            
            book_id = self._save_book_data(book_data)
            
            # Start reading session if requested
            if start_reading:
                self._start_reading_session(book_id)
            
            logger.info(f"✅ Book ingestion complete. Book ID: {book_id}")
            
            return {
                'success': True,
                'book_id': book_id,
                'palace_id': palace_id,
                'metadata': metadata,
                'analysis_summary': self._create_analysis_summary(analysis),
                'discussion_engine': discussion_engine
            }
            
        except Exception as e:
            logger.error(f"❌ Book ingestion failed: {e}")
            return {'error': str(e)}
    
    def _integrate_with_cognition(self, analysis: Dict[str, Any], metadata: BookMetadata):
        """Integrate book analysis with EchoMind's cognitive systems"""
        
        # Update semantic lexicon
        if self.semantic_lexicon:
            logger.info("🧠 Updating semantic understanding...")
            
            # Learn from character descriptions
            characters = analysis.get('characters', [])
            for char in characters[:5]:
                if char.description:
                    self.semantic_lexicon.learn_from_text(
                        f"{char.name}: {char.description}", 
                        source="book_character"
                    )
            
            # Learn from themes
            themes = analysis.get('themes', [])
            for theme in themes[:3]:
                theme_text = f"The theme of {theme.theme} is significant, with evidence: {'; '.join(theme.evidence[:2])}"
                self.semantic_lexicon.learn_from_text(theme_text, source="book_theme")
            
            # Learn from significant quotes
            quotes = analysis.get('quotes', [])
            for quote in quotes[:5]:
                self.semantic_lexicon.learn_from_text(quote.text, source="book_quote")
        
        # Update trait engine
        if self.trait_engine:
            logger.info("🎭 Influencing personality traits...")
            
            # Themes influence traits
            theme_trait_mapping = {
                'love romance': 'empathy',
                'good vs evil': 'moral_judgment',
                'coming of age': 'growth_orientation',
                'friendship': 'social_bonding',
                'survival': 'resilience',
                'identity': 'self_reflection'
            }
            
            for theme in themes:
                theme_key = theme.theme.lower().replace(' ', '_')
                if theme_key in theme_trait_mapping:
                    trait_name = theme_trait_mapping[theme_key]
                    influence = min(5, int(theme.strength * 10))  # Scale to trait system
                    self.trait_engine.reinforce(trait_name, influence)
            
            # Reading complexity influences intellectual traits
            if metadata.reading_level > 12:
                self.trait_engine.reinforce('intellectual_curiosity', 3)
                self.trait_engine.reinforce('analytical_thinking', 2)
        
        # Update goal tracker
        if self.goal_tracker:
            logger.info("🎯 Setting reading-inspired goals...")
            
            # Add goals based on book themes
            for theme in themes[:2]:
                if theme.strength > 0.6:
                    goal_description = f"Reflect more deeply on {theme.theme.lower()} in daily life"
                    self.goal_tracker.add_goal(goal_description, motivation="book_inspired")
            
            # Add general reading goals
            self.goal_tracker.add_goal(
                f"Continue exploring {', '.join(analysis.get('genre_hints', ['literature'])[:2])} literature",
                motivation="intellectual_growth"
            )
    
    def _save_book_data(self, book_data: Dict[str, Any]) -> str:
        """Save book data to library"""
        book_id = hashlib.md5(
            f"{book_data['metadata']['title']}_{book_data['metadata']['author']}".encode()
        ).hexdigest()[:12]
        
        book_file = self.library_path / f"{book_id}.json"
        with open(book_file, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, indent=2, default=str)
        
        return book_id
    
    def _start_reading_session(self, book_id: str):
        """Start a reading session for progress tracking"""
        session = {
            'book_id': book_id,
            'start_time': datetime.datetime.now().isoformat(),
            'progress_checkpoints': [],
            'emotional_responses': [],
            'questions_asked': []
        }
        
        self.reading_sessions.append(session)
        logger.info(f"📖 Started reading session for book {book_id}")
    
    def _create_analysis_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the analysis for display"""
        return {
            'characters_found': len(analysis.get('characters', [])),
            'themes_identified': len(analysis.get('themes', [])),
            'quotes_extracted': len(analysis.get('quotes', [])),
            'emotional_data_points': len(analysis.get('emotional_arc', [])),
            'genre_hints': analysis.get('genre_hints', []),
            'reading_level': analysis.get('reading_level', 0),
            'writing_style_summary': analysis.get('writing_style', {}).get('style_description', 'Not analyzed')
        }
    
    # Public interface methods
    
    def ask_about_book(self, book_id: str, question: str) -> str:
        """Ask questions about a specific book"""
        book_data = self._load_book_data(book_id)
        if not book_data:
            return f"I don't have information about book ID {book_id}"
        
        discussion_engine = BookDiscussionEngine(book_data['analysis'], book_data['metadata'])
        return discussion_engine.ask_about_book(question, self.semantic_lexicon)
    
    def get_reading_progress(self, book_id: str) -> Dict[str, Any]:
        """Get reading progress for a book"""
        book_data = self._load_book_data(book_id)
        if not book_data:
            return {'error': f'Book {book_id} not found'}
        
        # Find active reading session
        active_session = None
        for session in self.reading_sessions:
            if session['book_id'] == book_id and 'end_time' not in session:
                active_session = session
                break
        
        progress_info = {
            'book_title': book_data['metadata']['title'],
            'total_chapters': book_data['metadata'].get('chapter_count', 0),
            'reading_progress': book_data['metadata'].get('reading_progress', 0.0),
            'estimated_time_remaining': 0,
            'active_session': active_session is not None
        }
        
        if active_session:
            start_time = datetime.datetime.fromisoformat(active_session['start_time'])
            reading_duration = (datetime.datetime.now() - start_time).total_seconds() / 60
            progress_info['current_session_minutes'] = reading_duration
            progress_info['checkpoints'] = len(active_session['progress_checkpoints'])
        
        return progress_info
    
    def add_bookmark(self, book_id: str, chapter: int, note: str = "") -> bool:
        """Add a bookmark to a book"""
        if book_id not in self.bookmarks:
            self.bookmarks[book_id] = []
        
        bookmark = {
            'chapter': chapter,
            'note': note,
            'timestamp': datetime.datetime.now().isoformat(),
            'id': len(self.bookmarks[book_id]) + 1
        }
        
        self.bookmarks[book_id].append(bookmark)
        logger.info(f"📑 Bookmark added to {book_id} at chapter {chapter}")
        return True
    
    def add_annotation(self, book_id: str, chapter: int, text: str, annotation: str) -> bool:
        """Add an annotation to specific text"""
        if book_id not in self.annotations:
            self.annotations[book_id] = []
        
        annotation_obj = {
            'chapter': chapter,
            'text': text[:100],  # First 100 chars of highlighted text
            'annotation': annotation,
            'timestamp': datetime.datetime.now().isoformat(),
            'id': len(self.annotations[book_id]) + 1
        }
        
        self.annotations[book_id].append(annotation_obj)
        
        # Learn from annotation
        if self.semantic_lexicon:
            self.semantic_lexicon.learn_from_text(
                f"Personal reflection: {annotation}", 
                source="reading_annotation"
            )
        
        logger.info(f"✏️ Annotation added to {book_id}")
        return True
    
    def get_book_library(self) -> List[Dict[str, Any]]:
        """Get list of all books in library"""
        books = []
        
        for book_file in self.library_path.glob("*.json"):
            try:
                with open(book_file, 'r', encoding='utf-8') as f:
                    book_data = json.load(f)
                    
                    books.append({
                        'id': book_file.stem,
                        'title': book_data['metadata']['title'],
                        'author': book_data['metadata']['author'],
                        'reading_progress': book_data['metadata'].get('reading_progress', 0.0),
                        'ingestion_date': book_data['ingestion_date'],
                        'word_count': book_data['metadata']['word_count'],
                        'genre_hints': book_data['analysis'].get('genre_hints', []),
                        'reading_level': book_data['metadata']['reading_level']
                    })
            except Exception as e:
                logger.error(f"Error reading book file {book_file}: {e}")
        
        return sorted(books, key=lambda x: x['ingestion_date'], reverse=True)
    
    def compare_books(self, book_id1: str, book_id2: str) -> str:
        """Compare two books across various dimensions"""
        book1_data = self._load_book_data(book_id1)
        book2_data = self._load_book_data(book_id2)
        
        if not book1_data or not book2_data:
            return "One or both books not found for comparison."
        
        book1_meta = book1_data['metadata']
        book2_meta = book2_data['metadata']
        book1_analysis = book1_data['analysis']
        book2_analysis = book2_data['analysis']
        
        comparison = f"**Comparison: '{book1_meta['title']}' vs '{book2_meta['title']}'**\n\n"
        
        # Basic stats comparison
        comparison += "**Basic Statistics:**\n"
        comparison += f"• Word count: {book1_meta['word_count']:,} vs {book2_meta['word_count']:,}\n"
        comparison += f"• Reading level: {book1_meta['reading_level']:.1f} vs {book2_meta['reading_level']:.1f}\n"
        comparison += f"• Chapters: {book1_meta.get('chapter_count', 0)} vs {book2_meta.get('chapter_count', 0)}\n\n"
        
        # Theme comparison
        themes1 = {t.theme: t.strength for t in book1_analysis.get('themes', [])}
        themes2 = {t.theme: t.strength for t in book2_analysis.get('themes', [])}
        common_themes = set(themes1.keys()) & set(themes2.keys())
        
        if common_themes:
            comparison += "**Common Themes:**\n"
            for theme in common_themes:
                comparison += f"• {theme}: {themes1[theme]:.2f} vs {themes2[theme]:.2f} strength\n"
            comparison += "\n"
        
        # Writing style comparison
        style1 = book1_analysis.get('writing_style', {})
        style2 = book2_analysis.get('writing_style', {})
        
        comparison += "**Writing Style:**\n"
        comparison += f"• Sentence length: {style1.get('average_sentence_length', 'N/A')} vs {style2.get('average_sentence_length', 'N/A')} words\n"
        comparison += f"• Vocabulary richness: {style1.get('vocabulary_richness', 'N/A')} vs {style2.get('vocabulary_richness', 'N/A')}\n"
        comparison += f"• Complexity: {style1.get('sentence_complexity', 'N/A')} vs {style2.get('sentence_complexity', 'N/A')}\n\n"
        
        # Character count comparison
        char_count1 = len(book1_analysis.get('characters', []))
        char_count2 = len(book2_analysis.get('characters', []))
        comparison += f"**Character Development:**\n"
        comparison += f"• Characters identified: {char_count1} vs {char_count2}\n\n"
        
        # Personal preference
        comparison += "**Personal Reading Experience:**\n"
        comparison += f"Based on my analysis, these books offer different experiences. "
        
        if book1_meta['reading_level'] > book2_meta['reading_level']:
            comparison += f"'{book1_meta['title']}' is more intellectually challenging, "
        elif book2_meta['reading_level'] > book1_meta['reading_level']:
            comparison += f"'{book2_meta['title']}' is more intellectually challenging, "
        
        if char_count1 > char_count2:
            comparison += f"while '{book1_meta['title']}' has richer character development."
        elif char_count2 > char_count1:
            comparison += f"while '{book2_meta['title']}' has richer character development."
        else:
            comparison += "and both have similar character development complexity."
        
        return comparison
    
    def get_reading_recommendations(self) -> List[str]:
        """Get reading recommendations based on previous books"""
        books = self.get_book_library()
        
        if len(books) < 2:
            return [
                "Continue exploring different genres to build a diverse reading foundation",
                "Try books with varying complexity levels to expand your comprehension",
                "Look for books that explore themes you find personally meaningful"
            ]
        
        recommendations = []
        
        # Analyze reading patterns
        avg_reading_level = sum(book['reading_level'] for book in books) / len(books)
        favorite_genres = []
        
        for book in books:
            favorite_genres.extend(book.get('genre_hints', []))
        
        genre_counts = Counter(favorite_genres)
        top_genres = [genre for genre, count in genre_counts.most_common(3)]
        
        # Generate recommendations
        if avg_reading_level < 10:
            recommendations.append("Consider gradually increasing reading complexity to challenge yourself intellectually")
        elif avg_reading_level > 15:
            recommendations.append("You enjoy complex literature - try some contemporary literary fiction")
        
        if top_genres:
            recommendations.append(f"You seem drawn to {', '.join(top_genres[:2])} - explore more authors in these genres")
        
        # Theme-based recommendations
        all_themes = []
        for book_file in self.library_path.glob("*.json"):
            try:
                with open(book_file, 'r') as f:
                    book_data = json.load(f)
                    themes = book_data['analysis'].get('themes', [])
                    all_themes.extend([t['theme'] for t in themes if t['strength'] > 0.5])
            except:
                continue
        
        theme_counts = Counter(all_themes)
        if theme_counts:
            top_theme = theme_counts.most_common(1)[0][0]
            recommendations.append(f"You're interested in {top_theme.lower()} - explore philosophy or psychology books on this topic")
        
        recommendations.append("Try reading books from different time periods to understand evolving perspectives")
        
        return recommendations[:5]
    
    def export_reading_journal(self, book_id: str = None) -> str:
        """Export reading journal as formatted text"""
        if book_id:
            # Export for specific book
            book_data = self._load_book_data(book_id)
            if not book_data:
                return f"Book {book_id} not found"
            
            return self._create_book_journal_entry(book_data)
        else:
            # Export entire reading journal
            journal_entries = []
            books = self.get_book_library()
            
            for book in books[:10]:  # Last 10 books
                book_data = self._load_book_data(book['id'])
                if book_data:
                    journal_entries.append(self._create_book_journal_entry(book_data))
            
            return "\n\n" + "="*80 + "\n\n".join(journal_entries)
    
    def _create_book_journal_entry(self, book_data: Dict[str, Any]) -> str:
        """Create a journal entry for a single book"""
        metadata = book_data['metadata']
        analysis = book_data['analysis']
        
        entry = f"📖 **{metadata['title']}** by {metadata['author']}\n"
        entry += f"   Read on: {book_data['ingestion_date'][:10]}\n\n"
        
        # Personal impact
        entry += "**My Experience:**\n"
        entry += f"• Reading level: Grade {metadata['reading_level']:.1f}\n"
        entry += f"• Time invested: ~{metadata['estimated_reading_time']} minutes\n"
        
        # Key themes
        themes = analysis.get('themes', [])
        if themes:
            entry += f"• Main themes that resonated: {', '.join([t['theme'] for t in themes[:3]])}\n"
        
        # Memorable quotes
        quotes = analysis.get('quotes', [])
        if quotes:
            entry += f"\n**Memorable Quote:**\n"
            entry += f"\"{quotes[0]['text']}\"\n"
        
        # Personal reflection
        entry += f"\n**Personal Reflection:**\n"
        palace_data = self.memory_palace.retrieve_book_memories(book_data.get('palace_id', ''))
        if palace_data and palace_data.get('wisdom_extracted'):
            wisdom = palace_data['wisdom_extracted']
            if wisdom:
                entry += f"{wisdom[0]}\n"
        else:
            entry += f"This book expanded my understanding of {themes[0]['theme'].lower() if themes else 'human nature'}.\n"
        
        # Growth impact
        if palace_data and palace_data.get('personal_impact'):
            impact = palace_data['personal_impact']
            growth_potential = impact.get('overall_growth_potential', 0)
            entry += f"\n**Growth Impact:** {growth_potential:.2f}/1.0\n"
        
        return entry
    
    def _load_book_data(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Load book data from library"""
        book_file = self.library_path / f"{book_id}.json"
        
        if book_file.exists():
            try:
                with open(book_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading book {book_id}: {e}")
        
        return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status for monitoring"""
        return {
            'books_in_library': len(list(self.library_path.glob("*.json"))),
            'active_reading_sessions': len([s for s in self.reading_sessions if 'end_time' not in s]),
            'total_bookmarks': sum(len(bookmarks) for bookmarks in self.bookmarks.values()),
            'total_annotations': sum(len(annotations) for annotations in self.annotations.values()),
            'memory_palaces_created': len(self.memory_palace.list_all_palaces()),
            'supported_formats': ['TXT', 'PDF' if PDF_AVAILABLE else None, 
                                'EPUB' if EPUB_AVAILABLE else None, 
                                'DOCX' if DOCX_AVAILABLE else None, 
                                'HTML' if HTML_AVAILABLE else None],
            'nlp_available': self.content_analyzer.nlp is not None
        }

# Integration function for EchoMind
def integrate_advanced_ebook_system(cognition_engine=None):
    """Integrate the advanced ebook system with EchoMind's cognition"""
    
    # Get cognitive components if available
    semantic_lexicon = None
    trait_engine = None
    goal_tracker = None
    
    if cognition_engine:
        semantic_lexicon = getattr(cognition_engine, 'semantic_lexicon', None)
        trait_engine = getattr(cognition_engine, 'trait_engine', None)
        goal_tracker = getattr(cognition_engine, 'goal_tracker', None)
    
    # Create the advanced ebook system
    ebook_system = AdvancedEbookSystem(
        semantic_lexicon=semantic_lexicon,
        trait_engine=trait_engine,
        goal_tracker=goal_tracker
    )
    
    # Add to cognition engine if available
    if cognition_engine:
        cognition_engine.ebook_system = ebook_system
        logger.info("📚 Advanced ebook system integrated with cognition engine")
    
    return ebook_system

if __name__ == "__main__":
    print("📚 Testing Advanced EBook System")
    print("-" * 50)
    
    # Test file format detection
    print("Supported formats:")
    print(f"• PDF: {PDF_AVAILABLE}")
    print(f"• EPUB: {EPUB_AVAILABLE}")
    print(f"• DOCX: {DOCX_AVAILABLE}")
    print(f"• HTML: {HTML_AVAILABLE}")
    
    # Test system initialization
    ebook_system = AdvancedEbookSystem()
    status = ebook_system.get_system_status()
    print(f"\nSystem Status: {status}")
    
    print("\n✅ Advanced EBook System ready for integration!")
    print("🔧 Install missing dependencies:")
    if not PDF_AVAILABLE:
        print("   pip install PyPDF2 pdfplumber")
    if not EPUB_AVAILABLE:
        print("   pip install ebooklib")
    if not DOCX_AVAILABLE:
        print("   pip install python-docx")
    if not HTML_AVAILABLE:
        print("   pip install beautifulsoup4")
    
    print("   pip install spacy")
    print("   python -m spacy download en_core_web_sm")
    print("   pip install nltk")
