
## Part 1: Instructions for the Agent

### Purpose

* Your goal is to create code optimized for interpretation by future language-model agents (LLMs).
* You must explicitly encode semantic intent through multiple layers of **orthogonal semantic cues**.

### The 50% Rule

> **Every concept in your codebase must be represented by multiple independent semantic hints ("bits"), each with >50% likelihood of clearly expressing intent.**

#### Semantic Bit Definition

* A minimal, independent unit (comment, docstring, naming) clearly communicating intent without external context.

#### Requirements

* For each concept, provide **at least three distinct semantic bits**.
* Each semantic bit must differ enough from the others to provide independent clues about intent (orthogonality).
* Bits should each be understandable independently (permutation-friendly).

---
If you think of this coding job as a signal finding problem, the semantic bits increase the signal quality for future developers, making it a lot easier to grasp accurately the context.  
---

### Structural Requirements (Modularity)

* Each folder/module must contain its own **copy of this AGENTS.md** and have an identical layout structure, permitting modular reuse.
* Modules must explicitly export functionality; no hidden dependencies.
* Modules may import functionality at module scope, but every function **must explicitly pass all imported functionality via parameters**.
* **No function may reference any variable not explicitly defined within that same function’s scope.**

---

### Testing (Range → Expectation Contract)

* Every function must immediately precede a canonical "Range→Expectation" comment block.
* Clearly define the **input-range per variable**, split into discrete "cases," and the corresponding **expected output behavior** for each case.
* Testing framework will randomly generate inputs within each defined range-case to validate expected behavior.

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

Example:

```
# [RANGE-EXPECTATION]: divide_positive
# INPUT:
#   numerator:
#     case positive: x > 0 → normal division
#     case zero: x == 0 → returns 0
#     case negative: x < 0 → ValueError
#   denominator:
#     case positive: y > 0 → normal division
#     case zero: y == 0 → ZeroDivisionError
#     case negative: y < 0 → ValueError
# OUTPUT:
#   Performs normal division only if numerator and denominator are positive, else raises specified exceptions.
```

---

## Part 2: Linter Rules & Conventions

The following rules are enforced strictly by the linter. Violations fail builds immediately.

| ID   | Rule                                                                                                                      | Failure Message                                                            |
| ---- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| L001 | Each function must be preceded by `[RANGE-EXPECTATION]` block matching canonical format.                                  | `MISSING_RANGE_EXPECTATION:<function_name>`                                |
| L002 | No global or module-level mutable state is allowed. Variables must be function-scoped.                                    | `GLOBAL_STATE_VIOLATION:<variable_name>`                                   |
| L003 | Every function parameter must explicitly pass all required imports; no implicit imported variable usage inside functions. | `IMPLICIT_IMPORT_VIOLATION:<function_name>/<variable_name>`                |
| L004 | Each module must explicitly export functionality; no hidden or indirect dependencies.                                     | `MODULE_EXPORT_VIOLATION:<module_name>`                                    |
| L005 | Range-expectation block must define all parameters clearly and exhaustively per canonical format.                         | `RANGE_EXPECTATION_INCOMPLETE:<function_name>/<parameter_name>`            |
| L006 | Every input parameter's range-case must have a corresponding explicit expected behavior defined.                          | `CASE_EXPECTATION_UNDEFINED:<function_name>/<parameter_name>/<case_label>` |
| L007 | Testing must randomly sample inputs within each defined input range-case; deterministic randomness required.              | `NON_DETERMINISTIC_TESTING:<function_name>`                                |
| L008 | No function may access variables defined outside its own immediate function scope, even within the same module.           | `OUT_OF_SCOPE_VARIABLE:<function_name>/<variable_name>`                    |

---

**This AGENTS.md file itself must follow the 50% Rule. All updates must add at least three orthogonal semantic bits clearly encoding intended meaning.**
