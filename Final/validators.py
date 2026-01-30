"""
Validators Module for the MWAHAHA Humor Generation Pipeline.

Provides deterministic constraint satisfaction checks:
- Word inclusion verification for Task A2
- Character length limits
- Word count limits for Task B
- Language-specific validations
"""

import re
from typing import Tuple

from config import MAX_CHARS, MAX_WORDS_TASK_B
from logger import logger, log_constraint_check


def normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, strip whitespace)."""
    return text.lower().strip()


def check_word_inclusion(joke: str, word1: str, word2: str) -> Tuple[bool, dict]:
    """
    Check if both required words appear in the joke.
    
    Uses case-insensitive matching and handles word boundaries.
    
    Args:
        joke: The generated joke text
        word1: First required word
        word2: Second required word
    
    Returns:
        Tuple of (passed, details_dict)
    """
    normalized_joke = normalize_text(joke)
    normalized_word1 = normalize_text(word1)
    normalized_word2 = normalize_text(word2)
    
    # Use word boundary matching for accuracy
    # This handles cases like "hammer" not matching "hammered"
    # But we want "hammer" to match "hammer," or "hammer!"
    pattern1 = re.compile(r'\b' + re.escape(normalized_word1) + r'\b', re.IGNORECASE)
    pattern2 = re.compile(r'\b' + re.escape(normalized_word2) + r'\b', re.IGNORECASE)
    
    word1_found = bool(pattern1.search(joke))
    word2_found = bool(pattern2.search(joke))
    
    passed = word1_found and word2_found
    
    details = {
        f"'{word1}'": "✅ found" if word1_found else "❌ missing",
        f"'{word2}'": "✅ found" if word2_found else "❌ missing",
    }
    
    return passed, details


def check_char_length(text: str, language: str) -> Tuple[bool, dict]:
    """
    Check if text is within character limit for the language.
    
    Args:
        text: The generated text
        language: Language code ("en", "es", "zh", "b1", "b2")
    
    Returns:
        Tuple of (passed, details_dict)
    """
    max_chars = MAX_CHARS.get(language, 900)
    char_count = len(text)
    
    passed = char_count <= max_chars
    
    details = {
        "char_count": char_count,
        "max_allowed": max_chars,
        "status": "✅ within limit" if passed else f"❌ exceeded by {char_count - max_chars}",
    }
    
    return passed, details


def check_word_count(text: str, max_words: int = MAX_WORDS_TASK_B) -> Tuple[bool, dict]:
    """
    Check if text is within word count limit (for Task B).
    
    Args:
        text: The generated text
        max_words: Maximum allowed words
    
    Returns:
        Tuple of (passed, details_dict)
    """
    # Simple word count (split on whitespace)
    words = text.split()
    word_count = len(words)
    
    passed = word_count <= max_words
    
    details = {
        "word_count": word_count,
        "max_allowed": max_words,
        "status": "✅ within limit" if passed else f"❌ exceeded by {word_count - max_words}",
    }
    
    return passed, details


def check_not_empty(text: str) -> Tuple[bool, dict]:
    """
    Check if the generated text is not empty or just whitespace.
    
    Args:
        text: The generated text
    
    Returns:
        Tuple of (passed, details_dict)
    """
    passed = bool(text and text.strip())
    
    details = {
        "status": "✅ has content" if passed else "❌ empty or whitespace only",
    }
    
    return passed, details

class ConstraintValidator:
    """
    Validates generated jokes against task-specific constraints.
    
    Provides both individual checks and comprehensive validation.
    """
    
    def __init__(self, item_id: str):
        self.item_id = item_id
        self.results = []
    
    def add_check(self, name: str, passed: bool, details: dict):
        """Record a constraint check result."""
        self.results.append({
            "name": name,
            "passed": passed,
            "details": details,
        })
        log_constraint_check(self.item_id, name, passed, details)
    
    def all_passed(self) -> bool:
        """Check if all constraints passed."""
        return all(r["passed"] for r in self.results)
    
    def get_failures(self) -> list:
        """Get list of failed constraints."""
        return [r for r in self.results if not r["passed"]]
    
    def validate_task_a_headline(self, joke: str, language: str) -> bool:
        """
        Validate a Task A headline-based joke.
        
        Checks:
        - Not empty
        - Character limit
        - No placeholders
        """
        passed, details = check_not_empty(joke)
        self.add_check("not_empty", passed, details)
        
        passed, details = check_char_length(joke, language)
        self.add_check("char_length", passed, details)
        
        return self.all_passed()
    
    def validate_task_a_word_inclusion(
        self, joke: str, word1: str, word2: str, language: str
    ) -> bool:
        """
        Validate a Task A word-inclusion joke.
        
        Checks:
        - Not empty
        - Both words present
        - Character limit
        - No placeholders
        """
        passed, details = check_not_empty(joke)
        self.add_check("not_empty", passed, details)
        
        passed, details = check_word_inclusion(joke, word1, word2)
        self.add_check("word_inclusion", passed, details)
        
        passed, details = check_char_length(joke, language)
        self.add_check("char_length", passed, details)
        
        return self.all_passed()
    
    def validate_task_b(self, caption: str, task_type: str = "b1") -> bool:
        """
        Validate a Task B caption.
        
        Checks:
        - Not empty
        - Word count (max 20)
        - Character limit
        - No placeholders
        """
        passed, details = check_not_empty(caption)
        self.add_check("not_empty", passed, details)
        
        passed, details = check_word_count(caption)
        self.add_check("word_count", passed, details)
        
        passed, details = check_char_length(caption, task_type)
        self.add_check("char_length", passed, details)
        
        return self.all_passed()


def validate_joke(
    joke: str,
    task_type: str,
    language: str = "en",
    word1: str = None,
    word2: str = None,
    item_id: str = "",
) -> Tuple[bool, list]:
    """
    Main validation function for any task type.
    
    Args:
        joke: Generated joke/caption
        task_type: One of "a1" (headline), "a2" (word inclusion), "b1", "b2"
        language: Language code
        word1: Required word for A2 task
        word2: Required word for A2 task
        item_id: ID for logging
    
    Returns:
        Tuple of (all_passed, list_of_failures)
    """
    validator = ConstraintValidator(item_id)
    
    if task_type == "a1":
        validator.validate_task_a_headline(joke, language)
    elif task_type == "a2":
        if not word1 or not word2:
            logger.error(f"Word inclusion task requires word1 and word2")
            return False, [{"name": "missing_words", "details": "word1 or word2 not provided"}]
        validator.validate_task_a_word_inclusion(joke, word1, word2, language)
    elif task_type in ("b1", "b2"):
        validator.validate_task_b(joke, task_type)
    else:
        logger.error(f"Unknown task type: {task_type}")
        return False, [{"name": "unknown_task", "details": f"task_type={task_type}"}]
    
    return validator.all_passed(), validator.get_failures()
