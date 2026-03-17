"""
All 30 spec test cases for the name verifier.
Run with: pytest tests/test_verifier.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from verifier import verify


# ---------------------------------------------------------------------------
# Expected MATCHES (18 cases)
# ---------------------------------------------------------------------------

MATCH_CASES = [
    # Exact
    ("John Smith", "John Smith", "exact"),
    # Nickname variants
    ("Jon Smith", "John Smith", "Jon↔John nickname"),
    ("Johnny Smith", "John Smith", "Johnny↔John nickname"),
    ("Robert Johnson", "Bob Johnson", "Robert↔Bob nickname"),
    ("Liz Taylor", "Elizabeth Taylor", "Liz↔Elizabeth nickname"),
    ("Bill Clinton", "William Clinton", "Bill↔William nickname"),
    ("Michael Brown", "Mike Brown", "Michael↔Mike nickname"),
    ("Thomas Anderson", "Tom Anderson", "Thomas↔Tom nickname"),
    ("Alexander Hamilton", "Alex Hamilton", "Alexander↔Alex nickname"),
    ("Chris Evans", "Christopher Evans", "Chris↔Christopher nickname"),
    ("Sarah Connor", "Sara Connor", "Sarah↔Sara nickname"),
    ("Shawn Murphy", "Sean Murphy", "Shawn↔Sean nickname"),
    ("Ahmed Hassan", "Ahmad Hassan", "Ahmed↔Ahmad nickname"),
    ("Muhammad Ali", "Mohammed Ali", "Muhammad↔Mohammed nickname"),
    # Prefix / compound normalisation
    ("Al-Hassan", "Al Hassan", "al- prefix normalization"),
    ("McDonald", "MacDonald", "Mc/Mac normalization"),
    # Compound name join/split
    ("Abdul Rahman", "Abdulrahman", "compound join"),
    # Case-only difference
    ("Ali ibn Abi Talib", "Ali Ibn Abi Talib", "case normalization"),
]

# ---------------------------------------------------------------------------
# Expected NON-MATCHES (12 cases)
# ---------------------------------------------------------------------------

NOMATCH_CASES = [
    # Different first name
    ("John Smith", "Jane Smith", "different first name"),
    # Same-looking but distinct names
    ("Michael Jordan", "Michelle Jordan", "Michael≠Michelle"),
    ("Christopher Lee", "Christian Lee", "Christopher≠Christian"),
    ("Maria Santos", "Mario Santos", "Maria≠Mario gender variant"),
    ("Rashid Al-Amin", "Rashidi Al-Amin", "Rashid≠Rashidi extension"),
    # Order reversals
    ("Smith John", "John Smith", "first/last order reversal"),
    ("Ahmed Hassan", "Hassan Ahmed", "first/last order reversal 2"),
    ("Abdulrahman Khalid", "Khalid Abdulrahman", "compound order reversal"),
    # Not a nickname pair
    ("William Foster", "Liam Foster", "William≠Liam not a nickname"),
    # Unrelated names
    ("John Smith", "James Brown", "completely different names"),
    ("Anna Williams", "Maria Williams", "different first names"),
    ("Robert Chen", "Richard Chen", "Robert≠Richard (different nicknames)"),
]


# ---------------------------------------------------------------------------
# Parametrised tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("target,candidate,label", MATCH_CASES)
def test_expected_match(target, candidate, label):
    result = verify(target, candidate)
    assert result["match"] is True, (
        f"[{label}] Expected MATCH for ({target!r}, {candidate!r}) "
        f"but got match={result['match']}, confidence={result['confidence']:.3f}, "
        f"reason={result['reason']!r}"
    )


@pytest.mark.parametrize("target,candidate,label", NOMATCH_CASES)
def test_expected_nomatch(target, candidate, label):
    result = verify(target, candidate)
    assert result["match"] is False, (
        f"[{label}] Expected NO MATCH for ({target!r}, {candidate!r}) "
        f"but got match={result['match']}, confidence={result['confidence']:.3f}, "
        f"reason={result['reason']!r}"
    )
