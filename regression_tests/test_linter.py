# [RANGE-EXPECTATION]: test_self_lint ensures the linter validates itself
# INPUT section describes prerequisites for running this test.
#   none_param: placeholder showing no external modules are required.
#     case repository_run: when executed from the repository root → linter should lint all files without failure.
# OUTPUT clarifies the expected return status.
#   a zero exit code proves that both linting and all regression tests succeeded together.

def test_self_lint():
    """Ensure that the linter validates the repository without errors."""
    import linter
    import os
    import ast
    import re
    import random
    random.seed(0)
    assert linter.main(os, ast, re, random) == 0

__all__ = ['test_self_lint']
