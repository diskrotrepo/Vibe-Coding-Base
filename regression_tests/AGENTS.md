Here's the revised and complete **`AGENTS.md`** incorporating your final instructions clearly and precisely:

---

# AGENTS.md

---

## Part 1: Instructions for the Agent

### Purpose

* Your goal is to create code optimized for interpretation by future language-model agents (LLMs).
* You must explicitly encode semantic intent through multiple layers of **orthogonal semantic cues**.

### The 50% Rule

> **Every concept in your codebase must be represented by multiple independent semantic hints ("semantic bits"), each with >50% likelihood of clearly expressing intent.**

#### Semantic Bit Definition

* A minimal, independent unit (comment, docstring, naming) clearly communicating intent without external context.

#### Requirements

* For each concept, provide **at least three distinct semantic bits**.
* Each semantic bit must differ enough from the others to provide independent clues about intent (orthogonality).
* Bits should each be understandable independently (permutation-friendly).

---

If you think of coding as a signal-finding problem, semantic bits enhance the signal quality for future developers, making context easier to accurately grasp.

---

### Structural Requirements (Modularity)

* Each folder/module must contain its own **copy of this AGENTS.md** and have an identical layout structure, permitting modular reuse.
* Every project must include a `regression_tests` folder that also contains a verbatim copy of this file so the hierarchical structure remains intact.
* Modules must explicitly export functionality; no hidden dependencies.
* Modules may import functionality at module scope, but every function **must explicitly pass all imported functionality via parameters**.
* **No function may reference any variable not explicitly defined within that same function’s scope.**

---

### Commenting Requirements

* Every semantic bit encoded within the code (logic, naming, structure) **must have an explicit corresponding comment**.
* Comments must be written clearly and explicitly, fully communicating the intent behind each semantic bit.
* Comments should serve as independent semantic bits themselves, reinforcing clarity and signal quality.

---

### Testing (Range → Expectation Contract)

* **Every function must be immediately followed by its corresponding test function(s).** No other definitions or functions may intervene.
* Every function must immediately precede a canonical "Range→Expectation" comment block.
* Clearly define the **input-range per variable**, split into discrete "cases," and the corresponding **expected output behavior** for each case.
* The testing framework will randomly generate inputs within each defined range-case to validate expected behavior.

#### Canonical Range→Expectation Format:

```
# [RANGE-EXPECTATION]: <function_name>
# INPUT:
#   <param1>:
#     case <case_label>: <param1_condition> → <expected_behavior>
#     ...
#   <param2>:
#     case <case_label>: <param2_condition> → <expected_behavior>
#     ...
# OUTPUT:
#   <explicit description of expected outputs for each combination of input cases>
```

---

### Bug Response Protocol

* **Bugs** indicate more than just coding errors; they reveal missing or incorrect assumptions in your tests, documentation, or semantic explanations.
* When a bug is encountered:

  1. **Add** a failing test explicitly exposing the bug.
  2. **Extend** or **correct** the corresponding Range→Expectation block.
  3. **Add at least two additional semantic bits** (comments or documentation) clarifying the missed or misunderstood intent.
  4. **Commit** clearly indicating the bug and related documentation improvements.

---

## Part 2: Linter Rules & Conventions

The following rules are enforced strictly by the linter. Violations fail builds immediately.
The linter checks **all non-`.md` files, including itself**, refusing commits until all checks pass. The linter must also execute every regression test found across the repository and succeed before any commit is accepted. This linter is designed to lint itself so it can enforce the rules consistently.

| ID   | Rule                                                                                                                      | Failure Message                                                            |
| ---- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| L001 | Each function must be preceded by `[RANGE-EXPECTATION]` block matching canonical format.                                  | `MISSING_RANGE_EXPECTATION:<function_name>`                                |
| L002 | Every function definition must immediately be followed by its corresponding test definition(s).                           | `IMMEDIATE_TEST_MISSING:<function_name>`                                   |
| L003 | No global or module-level mutable state is allowed. Variables must be function-scoped.                                    | `GLOBAL_STATE_VIOLATION:<variable_name>`                                   |
| L004 | Every function parameter must explicitly pass all required imports; no implicit imported variable usage inside functions. | `IMPLICIT_IMPORT_VIOLATION:<function_name>/<variable_name>`                |
| L005 | Each module must explicitly export functionality; no hidden or indirect dependencies.                                     | `MODULE_EXPORT_VIOLATION:<module_name>`                                    |
| L006 | Range-expectation block must define all parameters clearly and exhaustively per canonical format.                         | `RANGE_EXPECTATION_INCOMPLETE:<function_name>/<parameter_name>`            |
| L007 | Every input parameter's range-case must have a corresponding explicit expected behavior defined.                          | `CASE_EXPECTATION_UNDEFINED:<function_name>/<parameter_name>/<case_label>` |
| L008 | Testing must randomly sample inputs within each defined input range-case; deterministic randomness required.              | `NON_DETERMINISTIC_TESTING:<function_name>`                                |
| L009 | No function may access variables defined outside its own immediate function scope, even within the same module.           | `OUT_OF_SCOPE_VARIABLE:<function_name>/<variable_name>`                    |
| L010 | Comments must be present at a minimum rate of 1 comment per every 3 lines of code.                                        | `INSUFFICIENT_COMMENT_DENSITY:<file_name>/<line_number>`                   |
| L011 | All comments must contain more than five words.                                                                           | `COMMENT_TOO_SHORT:<file_name>/<line_number>`                              |
| L012 | All comments within a file must be unique; no repeated comments allowed.                                                  | `DUPLICATE_COMMENT_FOUND:<file_name>/<line_number>`                        |

---

**This AGENTS.md file itself must follow the 50% Rule. All updates must add at least three orthogonal semantic bits clearly encoding intended meaning.**

Commit gating relies on this linter and every regression test. A commit may only land when both the linter and all regression tests run cleanly across the entire repository.
