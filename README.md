# Name Verification Application

> Engineering Take-Home

## Goal

A small application with two independent capabilities:

1. **Target name generation** from a user-provided prompt
2. **Candidate name verification** against the latest generated target name

**Key Design Constraint — The verifier must treat the generator as a black box.** It must not "cheat" by reusing generator chat context or calling back into the generator to decide whether a candidate matches.

---

## Functional Requirements

### Target Name Generator

**What the user can do:**
- Provide a free-form prompt (e.g., "Generate a random name with …")
- Trigger generation
- See the resulting target name (a single string)

**Behavior:**
- Each generation produces exactly one target name string
- The app maintains the concept of the latest generated target name
- Generating again updates what "latest" means

**Example prompt:** "Please generate a random Arabic sounding name with an Al and ibn both involved. The name shouldn't be longer than 5 words."

---

### Name Verifier

**What the user can do:**
- Input a candidate name
- Trigger verification
- Receive a structured result

**Result fields:**

| Field | Type | Description |
|-------|------|-------------|
| `match` | boolean | Whether the candidate matches the target |
| `confidence` | numeric (0–1 or 0–100) | Confidence score |
| `reason` | string | Short explanation |

- Checks candidate against the latest generated target name
- If no target name exists yet, returns a clear error state

---

## Architectural Constraint

> **Black Box Generator** — The verifier must be implemented as if the generator is not an open, available resource during verification. The verifier may only access the latest generated target name **string**.

Prohibited:
- Generator chat history or context
- Calling the generator again (directly or indirectly) to evaluate a match
- "Hidden" shared LLM state between generator and verifier

How the latest target name is exposed to the verifier (in memory, file, database, API, etc.) does not matter — only that the verifier is architecturally isolated from generator internals and operates using only the latest name string.

---

## Implementation

### Interface

Can be a web app, CLI app, desktop app, etc. A reviewer must be able to:
1. Provide a prompt → generate a target name
2. Provide a candidate name → verify against the latest target name and see output

### Matcher Evaluation

The verifier should:
- Produce deterministic (or at least stable/consistent) outputs
- Return `match` + `confidence` + `explanation`
- Be testable programmatically

---

## Test Cases

### Expected Matches

| # | Target Name | Candidate Name | Rationale |
|---|-------------|----------------|-----------|
| 1 | Tyler Bliha | Tlyer Bilha | Minor transposition and misspelling in both first and last name |
| 2 | Al-Hilal | alhilal | Hyphen and casing differences only |
| 3 | Dargulov | Darguloff | Common phonetic suffix variation (v vs ff) |
| 4 | Bob Ellensworth | Robert Ellensworth | Common nickname vs formal name |
| 5 | Mohammed Al Fayed | Muhammad Alfayed | Spacing and transliteration variance |
| 6 | Sarah O'Connor | Sara Oconnor | Apostrophe removal and vowel simplification |
| 7 | Jonathon Smith | Jonathan Smith | Common spelling variant of first name |
| 8 | Abdul Rahman ibn Saleh | Abdulrahman ibn Saleh | Spacing variation within compound name |
| 9 | Al Hassan Al Saud | Al-Hasan Al Saud | Minor consonant simplification and hyphenation |
| 10 | Katherine McDonald | Catherine Macdonald | Phonetic first name and common Mc/Mac variation |
| 11 | Yusuf Al Qasim | Youssef Alkasim | Transliteration differences in Arabic-derived names |
| 12 | Steven Johnson | Stephen Jonson | Phonetic spelling differences in both names |
| 13 | Alexander Petrov | Aleksandr Petrof | Slavic transliteration and phonetic variation |
| 14 | Jean-Luc Picard | Jean Luc Picard | Hyphen removal |
| 15 | Mikhail Gorbachov | Mikhail Gorbachev | Alternate transliteration endings |
| 16 | Elizabeth Turner | Liz Turner | Common nickname shortening |
| 17 | Omar ibn Al Khattab | Omar Ibn Alkhattab | Case, spacing, and compound-name variance |
| 18 | Sean O'Brien | Shawn Obrien | Phonetic first name and punctuation removal |

### Expected Non-Matches

| # | Target Name | Candidate Name | Rationale |
|---|-------------|----------------|-----------|
| 19 | Emanuel Oscar | Belinda Oscar | Same last name but entirely different first name |
| 20 | Michael Thompson | Michelle Thompson | Similar-looking but distinct first names |
| 21 | Ali Hassan | Hassan Ali | Token order swap changes identity |
| 22 | John Smith | James Smith | Different common first names |
| 23 | Abdullah ibn Omar | Omar ibn Abdullah | Reversal of patronymic meaning |
| 24 | Maria Gonzalez | Mario Gonzalez | Gendered name difference |
| 25 | Christopher Nolan | Christian Nolan | Similar prefix but distinct names |
| 26 | Ahmed Al Rashid | Ahmed Al Rashidi | Different surname root |
| 27 | Samantha Lee | Samuel Lee | Different first name despite shared root |
| 28 | Ivan Petrov | Ilya Petrov | Distinct given names in same cultural group |
| 29 | Fatima Zahra | Zahra Fatima | Name order inversion changes identity |
| 30 | William Carter | Liam Carter | Nickname not universally equivalent without explicit mapping |

---

## How to Run

> Setup and run instructions will be added here once the implementation is complete.
