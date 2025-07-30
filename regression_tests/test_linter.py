# [RANGE-EXPECTATION]: test_self_lint expectation block ensures self lint works
# INPUT SECTION DESCRIBING PARAMETERS REQUIRED BY THIS TEST CASE:
#   os_mod: operating system reference supplied to linter main call
#     case module: repository execution environment → linter completes run
#   ast_mod: abstract syntax tree module for parsing
#     case module: structural inspection library → supports linter analysis
#   re_mod: regular expression module for pattern detection
#     case module: regex library → facilitates comment parsing
#   random_mod: seeded randomness provider for deterministic run
#     case module: randomness engine → ensures predictable behavior
# OUTPUT DETAILS FOLLOWING EXECUTION PATH FOR SUCCESSFUL RUN:
#   numeric zero indicating successful self lint process

def test_self_lint():
    """Ensure that the linter validates the repository without errors."""
    import linter
    import os
    import ast
    import re
    import random
    random.seed(0)
    assert linter.main(os, ast, re, random, include_self_test=False) == 0

__all__ = [
    'test_self_lint',
]
