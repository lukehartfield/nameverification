"""
verifier.py — Multi-signal algorithmic name matching engine.

Exports a single function:
    verify(target: str, candidate: str) -> dict
"""

import re
import sys
import os

import jellyfish

sys.path.insert(0, os.path.dirname(__file__))
from names_data import NICKNAME_LOOKUP, COMPOUND_SPLITS, PREFIX_NORMALIZATIONS

# ---------------------------------------------------------------------------
# Known distinct name pairs that share phonetic codes but are different names.
# When BOTH tokens in a pair appear in this set AND they are NOT in the same
# nickname group, we treat them as non-matching regardless of JW / phonetic.
# ---------------------------------------------------------------------------
KNOWN_DISTINCT_NAMES = {
    "michael", "michelle",
    "daniel", "danielle",
    "christian", "christina", "christiana",
    "julian", "julia", "julie",
    "mario", "maria",
    "marco", "marca",
    "carlo", "carla",
    "aldo", "alda",
    "leo", "lea",
    "joel", "joela",
    "rafael", "rafaela",
    "gabriel", "gabriela",
    "samuel", "samuela",
    "pascal", "pascale",
    "marc", "marca",
    "alex", "alexa",
    "john", "jane",
    "anna", "anne",
}

# Vowels used in gender-variant final-char check
_VOWELS = set("aeiou")


# ---------------------------------------------------------------------------
# Step 1: Normalise a full name string
# ---------------------------------------------------------------------------

def _normalize(name: str) -> str:
    """Lowercase, strip punctuation, normalise whitespace, apply prefix rules."""
    s = name.lower()
    # Strip apostrophes and hyphens (but keep spaces so tokens stay separate)
    s = s.replace("'", "").replace("-", " ")
    # Remove remaining non-alphanumeric, non-space chars
    s = re.sub(r"[^a-z0-9 ]", "", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # Mc/Mac normalisation: replace leading "mc" token with "mac"
    tokens = s.split()
    normalised = []
    for tok in tokens:
        if tok.startswith("mc") and len(tok) > 2:
            tok = "mac" + tok[2:]
        normalised.append(tok)
    s = " ".join(normalised)
    # al- / al  prefix: "al hassan" → "alhassan", "al-hassan" already hyphen-stripped
    # We handle "al " as a separate prefix token in tokenisation, not here.
    return s


# ---------------------------------------------------------------------------
# Step 2: Tokenise & handle compound names
# ---------------------------------------------------------------------------

def _split_compounds(tokens: list) -> list:
    """Expand any token that is a known compound into its constituent parts."""
    result = []
    for tok in tokens:
        if tok in COMPOUND_SPLITS:
            result.extend(COMPOUND_SPLITS[tok])
        else:
            result.append(tok)
    return result


def _join_adjacent(tokens: list) -> list:
    """
    Try all adjacent pair joins and replace with compound if it appears in
    COMPOUND_SPLITS.  Returns the first successful join (leftmost).
    """
    if len(tokens) < 2:
        return tokens
    result = list(tokens)
    i = 0
    while i < len(result) - 1:
        joined = result[i] + result[i + 1]
        if joined in COMPOUND_SPLITS:
            result = result[:i] + COMPOUND_SPLITS[joined] + result[i + 2:]
        i += 1
    return result


def _tokenize(name: str) -> list:
    """Normalise and tokenise a name, expanding compounds."""
    norm = _normalize(name)
    tokens = norm.split()
    tokens = _normalize_prefix_tokens(tokens)
    tokens = _join_adjacent(tokens)
    tokens = _split_compounds(tokens)
    return tokens


def _normalize_prefix_tokens(tokens: list) -> list:
    """Canonicalize known prefixes so spaced and joined forms compare equally."""
    normalized = []
    i = 0

    while i < len(tokens):
        token = tokens[i]
        if token == "al" and i + 1 < len(tokens):
            normalized.append(f"al{tokens[i + 1]}")
            i += 2
            continue

        normalized.append(token)
        i += 1

    return normalized


# ---------------------------------------------------------------------------
# Helper: check if two tokens are in the same nickname group
# ---------------------------------------------------------------------------

def _in_same_nickname_group(tok1: str, tok2: str) -> bool:
    g1 = NICKNAME_LOOKUP.get(tok1)
    g2 = NICKNAME_LOOKUP.get(tok2)
    if g1 is None or g2 is None:
        return False
    # The NICKNAME_LOOKUP maps each name to the SAME frozenset/set object for its group
    return g1 is g2 or tok2 in g1 or tok1 in g2


# ---------------------------------------------------------------------------
# Step 3: Per-token score
# ---------------------------------------------------------------------------

def _token_score(tok1: str, tok2: str):
    """
    Returns (score, reason_tag) for a single token pair.
    reason_tag is one of: 'exact', 'nickname', 'phonetic', 'fuzzy'
    """
    if tok1 == tok2:
        return 1.0, "exact"

    in_group = _in_same_nickname_group(tok1, tok2)
    if in_group:
        return 0.95, "nickname"

    jw = jellyfish.jaro_winkler_similarity(tok1, tok2)
    m1 = jellyfish.metaphone(tok1)
    m2 = jellyfish.metaphone(tok2)
    phonetic_match = bool(m1 and m2 and m1 == m2)

    if phonetic_match:
        score = min(jw * 1.15, 1.0)
        tag = "phonetic"
    else:
        score = jw
        tag = "fuzzy"

    return score, tag


# ---------------------------------------------------------------------------
# Step 5: Special-case penalties (applied before threshold)
# ---------------------------------------------------------------------------

def _gender_variant_penalty(tok1: str, tok2: str) -> bool:
    """
    Return True if the token pair looks like a gender variant:
    - same length or differ by 1
    - differ only in the final character
    - that final character difference is a vowel swap (a↔o, a↔e, o↔a, e↔a, etc.)
    - both tokens are <= 7 chars
    - NOT in same nickname group
    """
    if _in_same_nickname_group(tok1, tok2):
        return False
    if len(tok1) > 7 or len(tok2) > 7:
        return False
    # Must differ only in final char (same prefix)
    if len(tok1) != len(tok2):
        return False
    if tok1[:-1] != tok2[:-1]:
        return False
    c1, c2 = tok1[-1], tok2[-1]
    return c1 in _VOWELS and c2 in _VOWELS and c1 != c2


def _substring_extension_penalty(tok1: str, tok2: str) -> bool:
    """
    Return True if one token is a strict prefix of the other and
    the extension is >= 1 char AND the shorter token has >= 4 chars.
    (Catches rashid/rashidi, etc.)
    """
    if tok1 == tok2:
        return False
    shorter, longer = (tok1, tok2) if len(tok1) < len(tok2) else (tok2, tok1)
    if len(shorter) < 4:
        return False
    if longer.startswith(shorter):
        return True
    return False


def _is_known_distinct_pair(tok1: str, tok2: str) -> bool:
    """
    Return True if both tokens are in KNOWN_DISTINCT_NAMES and are NOT
    in the same nickname group.
    """
    if tok1 in KNOWN_DISTINCT_NAMES and tok2 in KNOWN_DISTINCT_NAMES:
        if not _in_same_nickname_group(tok1, tok2):
            return True
    return False


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def verify(target: str, candidate: str) -> dict:
    """
    Compare two name strings and return a match decision.

    Returns:
        {
            "match": bool,
            "confidence": float,   # 0.0 – 1.0
            "reason": str          # human-readable explanation
        }
    """
    # --- Step 1 & 2: Tokenise ---
    toks_a = _tokenize(target)
    toks_b = _tokenize(candidate)

    # --- Order-reversal check ---
    # If the normalised token SETS are equal but the LISTS are different
    # (and both have >= 2 tokens), that means the words are the same but
    # in a different order — we treat this as a non-match.
    if (
        len(toks_a) >= 2
        and len(toks_b) >= 2
        and sorted(toks_a) == sorted(toks_b)   # same multiset
        and toks_a != toks_b                    # different order
    ):
        return {
            "match": False,
            "confidence": 0.1,
            "reason": "Token order reversal detected",
        }

    # --- Step 3 & 4: Align tokens and score ---
    # Pair tokens positionally up to the shorter list's length.
    min_len = min(len(toks_a), len(toks_b))
    max_len = max(len(toks_a), len(toks_b))

    token_scores = []
    token_tags = []
    token_weights = []
    penalty_reasons = []   # track special-case penalty descriptions

    # Track the best nickname/phonetic reason for the reason string
    best_nick_pair = None
    any_phonetic = False

    for i in range(min_len):
        t1 = toks_a[i]
        t2 = toks_b[i]
        score, tag = _token_score(t1, t2)

        # --- Special-case penalties on this token pair ---
        if tag != "exact" and tag != "nickname":
            # Gender variant check
            if _gender_variant_penalty(t1, t2):
                score *= 0.35
                penalty_reasons.append(f"gender variant ({t1}/{t2})")

            # Substring extension check
            elif _substring_extension_penalty(t1, t2):
                score *= 0.35
                penalty_reasons.append(f"substring extension ({t1}/{t2})")

            # Known distinct name pair
            elif _is_known_distinct_pair(t1, t2):
                score = 0.0
                penalty_reasons.append(f"known distinct names ({t1}/{t2})")

            # High JW but no phonetic match (catches Christopher/Christian)
            elif (
                tag == "fuzzy"
                and jellyfish.jaro_winkler_similarity(t1, t2) > 0.80
            ):
                score -= 0.10
                penalty_reasons.append(f"phonetic mismatch penalty ({t1}/{t2})")

        # Track reason metadata
        if tag == "nickname" and best_nick_pair is None:
            best_nick_pair = (t1, t2)
        if tag == "phonetic":
            any_phonetic = True

        weight = max(len(t1), len(t2))
        token_scores.append(score)
        token_tags.append(tag)
        token_weights.append(weight)

    # Unmatched tokens (length mismatch)
    n_unmatched = max_len - min_len
    for i in range(n_unmatched):
        # Use a small but non-zero weight so short extra tokens hurt less
        token_scores.append(0.3)
        token_weights.append(3)
        token_tags.append("unmatched")

    # Weighted average
    if not token_weights:
        confidence = 0.0
    else:
        total_weight = sum(token_weights)
        confidence = sum(s * w for s, w in zip(token_scores, token_weights)) / total_weight

    # Per extra token penalty
    if n_unmatched:
        confidence *= (0.85 ** n_unmatched)

    confidence = max(0.0, min(1.0, confidence))

    # If first-name token is a weak fuzzy match (not exact/nickname), penalize the
    # overall score so matching last names don't carry a mismatched first name.
    if (
        len(token_scores) >= 2
        and token_tags[0] not in ("exact", "nickname")
        and token_scores[0] < 0.70
    ):
        confidence *= 0.85

    confidence = max(0.0, min(1.0, confidence))

    # --- Step 6: Threshold & reason ---
    match = confidence >= 0.80

    # Build reason string
    if all(t == "exact" for t in token_tags):
        reason = "Exact match"
    elif best_nick_pair is not None:
        t1, t2 = best_nick_pair
        reason = f"Nickname match: {t1} → {t2}"
    elif any_phonetic and match:
        reason = f"Phonetic match (confidence: {confidence:.0%})"
    elif penalty_reasons:
        reason = f"Names are distinct — {'; '.join(penalty_reasons)} (confidence: {confidence:.0%})"
    elif match:
        reason = f"Names match (confidence: {confidence:.0%})"
    else:
        reason = f"Names are distinct (confidence: {confidence:.0%})"

    return {
        "match": match,
        "confidence": round(confidence, 4),
        "reason": reason,
    }
