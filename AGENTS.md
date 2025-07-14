# AGENTS.md – LLM‑First Project Guide

> **Why this document exists**\
> Large‑language models excel at pattern‑matching across text they have already seen, but they degrade when context is sparse, contradictory, or hidden behind implicit conventions.  This guide encodes an *LLM‑first* philosophy: every artefact in the repository—code, tests, docs, commit messages, even filenames—should emit clear, layered cues (“semantic bits”) that future human or AI contributors can fuse into an unambiguous mental model.

---

## 1. Core Principles

| Principle                         | Intent                                                                                                                                                               |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Signal Richness**               | Embed multiple, orthogonal hints about the same concept (see §2 “50 % Rule”).                                                                                        |
|                                   |                                                                                                                                                                      |
| **Explicit Reasoning Trail**      | Document *why* a design exists, not only *what* it does—understanding the rationale is itself a semantic cue.                                                        |
|                                   |                                                                                                                                                                      |
| **Dependency Minimalism**         | Prefer zero external dependencies; rely on the host language's standard library and built‑in assertions so every line remains transparent to the LLM.                |
|                                   |                                                                                                                                                                      |
| **Test Map Fidelity**             | Maintain a living map of *unique* input states and expected outputs, written in natural language and enforced by tests that embody the 50 % Rule.                    |
|                                   |                                                                                                                                                                      |
| **Bug‑Driven Scaffolding Repair** | Every bug triggers: **(1)** a regression test, **(2)** an update to the I/O map, **(3)** injection of new semantic bits to guard against the entire class of errors. |


---

## 2. The 50 % Rule (Correct Definition)

> *Compose many fragments that each have ****> 50 %**** chance of conveying the right intent.*\
> *Combine them so the joint probability of misunderstanding falls exponentially.*

### 2.1 Semantic Bits

A **semantic bit** is the smallest self‑contained phrase, token sequence or code annotation that preserves a sliver of intent.  Examples:

- docstring that states a function’s side‑effects
- a unit test asserting boundary behavior
- a comment mapping UI elements to model inputs
- an explanatory commit title

### 2.2 Practical Checklist

1. **Diversity** – Express every new concept *at least three* different ways (comment, test, README snippet, etc.).
2. **Orthogonality** – Ensure each bit reframes the information in a unique way that is likely to make it "click" for a different individual/learner; avoid lazy or low effort restatements.
3. **Permutation Friendly** – Order and wording may change later; keep each bit context‑independent.
4. **Verification** – Link bits through tests or lints so drift is detected automatically.

This approach prevents over‑fitting to one phrasing and keeps the project robust as different LLM versions traverse the repo.

---

## 3. Recommended Repository Skeleton

```
├── AGENTS.md   # Philosophy & rules
├── README.md   # Quick‑start narrative
└── project.ext # Monolithic source: code, tests, docs, I/O map
```

> Monolithic Philosophy\
> **Always one file—no exceptions.** Even for large codebases, keep all logic, tests, and docs in a single well‑structured source file. High‑granularity comments, formatted with the 50 % Rule, replace the need for modules.\
> To preserve navigability as the file grows, include (1) a top‑of‑file table of contents, (2) clearly delimited section headers (e.g., `#### DATA LAYER`), and (3) frequent semantic‑bit annotations that help vector search align with intent.

---

## 4. Coding Conventions

- **Indentation**: 2 spaces, no tabs, trim trailing whitespaces.
- **Top‑Matter TOC**: Each significant file begins with a short table of contents comment block.
- **Pure Functions First**: List pure, side‑effect‑free helpers before IO‑heavy.
- **Self‑Describing Names**: Avoid abbreviations unless they are domain jargon.
- **Error Narratives**: Error messages should teach; include action items.
- **Internationalization**: Externalize user‑visible strings early; LLMs can translate docs when keys are consistent.

---

## 5. Documentation Layers (In‑File)

| Layer | In‑file Segment                     | Purpose                                           |
| ----- | ----------------------------------- | ------------------------------------------------- |
| 0     | **Inline Microtest** (`assert ...`) | Immediate validation & semantic bit               |
| 1     | **Code Comment**                    | Clarify a single line or block of logic           |
| 2     | **Docstring**                       | Describe API surface and rationale                |
| 3     | **I/O Map Header**                  | Natural‑language matrix of state → expectation    |
| 4     | **ADR Log Section**                 | Persistent design‑decision journal at end of file |

An LLM that misses one layer will likely catch another, maintaining continuity while staying 100 % monolithic.

---

## 6. Commit & PR Template (excerpt)

```
### What & Why
<one‑sentence imperative summary>

### Changes
- [x] Semantic bit 1 – README example
- [x] Semantic bit 2 – unit test
- [x] Semantic bit 3 – inline comment

### Verification
`make test` passes (112 tests, 0 new warnings)
```

---

## 7. Input‑Output Map & Test Philosophy

### 7.1 Living Input‑Output Map

- Each public interface must be represented in a *plain‑language* table at the top of the monolithic file (`# I/O MAP`).  Each row records a unique pre‑state → post‑state expectation.
- Row text forms a semantic bit; phrase it distinctly so that a vector search for the scenario will surface it.

### 7.2 Regression & Coverage

- For **every** map entry there is a corresponding coded test.  Use the language’s built‑in `assert` mechanism (or equivalent) rather than an external test framework.
- When a bug appears, first *extend the map* with the failing scenario, then add a failing test in the regression section.  Only *after* that do you patch the implementation.

### 7.3 Tests as Semantic Cues

- **Names read like prose**: `should_reject_token_when_signature_invalid()`
- **Assertions embed rationale**: `assert err.code == "JWT_EXPIRED", "Token validation must fail fast to prevent replay"`
- Duplicate key phrases from the map in comments so each test contributes another > 50 % semantic bit.

### 7.4 Inline Microtests (“Buddy Asserts”)

Place quick sanity checks immediately after a function so the behavior is documented *and* verified in situ.

```python
def is_leap(year: int) -> bool:
    """Return True if *year* is a leap year (Gregorian)."""
    result = (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))

    # Layer 0 — microtests (50 % rule semantic bits)
    assert is_leap(2000) is True, "Year 2000 should be leap"
    assert is_leap(1900) is False, "Century not divisible by 400 is not leap"
    return result
```

These buddy asserts give instant feedback during development and serve as additional semantic bits, before the more formal map‑driven tests further down.

---

## 8. Bug Response Protocol

1. **Reproduce via Test** – Create or modify a test that fails, linked to a new I/O map row.
2. **Patch Functionality** – Fix code; ensure *all* tests pass.
3. **Scaffolding Repair** – Add at least two new semantic cues (comment, docstring, ADR snippet) describing *why* this bug slipped through and how future iterations should avoid the class.
4. **Retrospective Note** – In the commit message, tag `#regression` and outline the cues added.

---

---

## 9. Glossary

- **LLM‑First** – Designing artefacts optimised for language‑model comprehension.
- **Semantic Bit** – Minimal token sequence carrying intent (see §2).
- **50 % Rule** – Probability amplification via multiple >50 % bits.
- **Signal Richness** – Aggregate interpretative scope across bits.

---

---

*Maintained according to the 50 % Rule: every update must increase clarity in at least three dimensions (code, docs, tests).*

