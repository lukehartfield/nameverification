"""
Name generator for the name verification app.
Generates plausible names based on cultural and structural hints in prompts.
"""

import random
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from names_data import NAME_PARTS


def generate(prompt: str) -> str:
    """
    Parse prompt for hints and generate a plausible name.
    Returns a single name string.
    """
    prompt_lower = prompt.lower()

    # Step 1: Detect culture from keywords
    culture = _detect_culture(prompt_lower)

    # Step 2: Parse for structural hints
    has_al_prefix = _check_al_prefix(prompt_lower)
    has_ibn = _check_ibn(prompt_lower)
    has_mac_prefix = _check_mac_prefix(prompt_lower)

    # Step 3: Parse for length constraints
    max_words = _parse_max_words(prompt_lower)
    full_name_requested = _check_full_name(prompt_lower)
    first_name_only = _check_first_name_only(prompt_lower)

    # Step 4: Assemble the name based on culture
    if culture == "arabic":
        name = _generate_arabic_name(has_al_prefix, has_ibn, max_words, first_name_only, full_name_requested)
    elif culture == "slavic":
        name = _generate_slavic_name(max_words, first_name_only, full_name_requested)
    else:  # western or default
        name = _generate_western_name(has_mac_prefix, max_words, first_name_only, full_name_requested)

    return name


def _detect_culture(prompt_lower: str) -> str:
    """Detect culture from keywords in the prompt."""
    # Arabic keywords
    arabic_keywords = ["arabic", "arab", "muslim", "middle east", "al-", "ibn", "bin"]
    if any(keyword in prompt_lower for keyword in arabic_keywords):
        return "arabic"

    # Slavic keywords
    slavic_keywords = ["slavic", "russian", "polish", "czech", "serbian", "ukrainian"]
    if any(keyword in prompt_lower for keyword in slavic_keywords):
        return "slavic"

    # Western keywords
    western_keywords = ["western", "english", "american", "european", "french", "german"]
    if any(keyword in prompt_lower for keyword in western_keywords):
        return "western"

    # Default: randomly pick from all cultures
    return random.choice(["arabic", "slavic", "western"])


def _check_al_prefix(prompt_lower: str) -> bool:
    """Check if 'al ' or 'al-' prefix is requested."""
    return "al " in prompt_lower or "al-" in prompt_lower


def _check_ibn(prompt_lower: str) -> bool:
    """Check if 'ibn' is requested in the name."""
    return "ibn" in prompt_lower


def _check_mac_prefix(prompt_lower: str) -> bool:
    """Check if 'mc' or 'mac' prefix is requested for last name."""
    return "mc" in prompt_lower or "mac" in prompt_lower


def _parse_max_words(prompt_lower: str) -> int:
    """Parse for length constraints like 'no longer than X words'."""
    # Match patterns like "no longer than 2 words", "at most 3 words", "max 1 word"
    patterns = [
        r"should\s*not be longer than (\d+) words?",
        r"shouldn't be longer than (\d+) words?",
        r"no longer than (\d+) words?",
        r"at most (\d+) words?",
        r"max (\d+) words?"
    ]

    for pattern in patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            return int(match.group(1))

    return None  # No constraint


def _check_full_name(prompt_lower: str) -> bool:
    """Check if 'full name' or 'complete name' is requested."""
    return "full name" in prompt_lower or "complete name" in prompt_lower


def _check_first_name_only(prompt_lower: str) -> bool:
    """Check if 'first name only' is requested."""
    return "first name only" in prompt_lower


def _generate_arabic_name(has_al: bool, has_ibn: bool, max_words: int, first_only: bool, full_name: bool) -> str:
    """Generate an Arabic name based on constraints."""
    first = random.choice(NAME_PARTS["arabic_first"])

    # If first name only requested, return just the first name
    if first_only:
        if has_al:
            return f"al-{first}"
        return first

    # Handle "ibn" construction if requested
    if has_ibn:
        middle = random.choice(NAME_PARTS["arabic_middle"])
        name = f"{first} ibn {middle}"
        word_count = 3

        # If full name requested and we have room, add a last name (use another first name as last)
        if full_name and (max_words is None or word_count < max_words):
            last = random.choice(NAME_PARTS["arabic_first"])
            name = f"{name} {last}"

        if has_al:
            # Apply al- prefix to the first part without discarding any added surname
            suffix = name[len(first):]
            name = f"al-{first}{suffix}"
    else:
        # Standard structure: first + last (or first + last_ish)
        last = random.choice(NAME_PARTS["arabic_first"])  # Using first names as last names
        name = f"{first} {last}"
        word_count = 2

        if has_al:
            name = f"al-{first} {last}"

    # Respect max_words constraint
    if max_words is not None:
        tokens = name.split()
        if len(tokens) > max_words:
            name = " ".join(tokens[:max_words])

    return name


def _generate_slavic_name(max_words: int, first_only: bool, full_name: bool) -> str:
    """Generate a Slavic name based on constraints."""
    first = random.choice(NAME_PARTS["slavic_first"])

    # If first name only requested, return just the first name
    if first_only:
        return first

    # Generate last name (use the slavic_last pool)
    last = random.choice(NAME_PARTS["slavic_last"])
    name = f"{first} {last}"

    # Respect max_words constraint
    if max_words is not None:
        tokens = name.split()
        if len(tokens) > max_words:
            name = " ".join(tokens[:max_words])

    return name


def _generate_western_name(has_mac: bool, max_words: int, first_only: bool, full_name: bool) -> str:
    """Generate a Western name based on constraints."""
    first = random.choice(NAME_PARTS["western_first"])

    # If first name only requested, return just the first name
    if first_only:
        return first

    # Generate last name
    last = random.choice(NAME_PARTS["western_last"])

    # Apply Mac/Mc prefix if requested
    if has_mac:
        last = f"Mac{last}"

    name = f"{first} {last}"

    # Respect max_words constraint
    if max_words is not None:
        tokens = name.split()
        if len(tokens) > max_words:
            name = " ".join(tokens[:max_words])

    return name
