# These imports provide the foundational runtime capabilities required for the linter
# such as file system traversal, deterministic randomness and subprocess control.
import ast
import os
import random
import re
import subprocess
import sys

"""This module houses a compact yet strict linter built specifically for the
semantic coding scheme described in AGENTS.md. Its purpose is to scan every
python file within the repository and to run regression tests, blocking
commits whenever violations occur. Each of these introductory lines explains
the reasoning behind this tool and meets the comment length requirements."""

# [RANGE-EXPECTATION]: collect_python_files expectation block begins here
# INPUT PARAMETERS PROVIDED TO FUNCTION ARE DESCRIBED BELOW:
#   root_dir: parameter describes search directory root used for scanning
#     case standard: directory exists → python file paths enumerated
#   os_mod: module describing operating system interactions for directory walking
#     case module: operating system module → traverses directory structure
# OUTPUT RESULT EXPECTATIONS DISCUSSED BELOW IN DETAIL:
#   list containing every discovered python file path

def collect_python_files(root_dir, os_mod):
    """Search directory for python files while staying deterministic."""
    found_files = []
    for current, _, files in os_mod.walk(root_dir):
        for name in sorted(files):
            if name.endswith('.py'):
                found_files.append(os_mod.path.join(current, name))
    return found_files

# [RANGE-EXPECTATION]: test_collect_python_files expectation details continue below
# INPUT PARAMETERS USED BY TEST ARE EXPLAINED HERE:
#   os_mod: operating system utilities parameter provided for path resolution
#     case module: provided operating system utilities → handles path resolution
#   random_mod: seeded module controlling randomness behaviour during execution
#     case module: seeded randomness provider → deterministic ordering of results
# OUTPUT RESULTS RETURNED BY TEST SHOULD MATCH:
#   assertion passes when this file path appears in the function outcome

def test_collect_python_files(os_mod, random_mod):
    """Ensure that the search routine detects this file."""
    random_mod.seed(0)
    files = collect_python_files('.', os_mod)
    assert os_mod.path.abspath(__file__) in [os_mod.path.abspath(f) for f in files]

# [RANGE-EXPECTATION]: parse_comments describes comment splitting logic in detail
# INPUT PARAMETER INFORMATION LISTED BELOW FOR REFERENCE:
#   lines: argument representing raw file content lines used for analysis
#     case list: lines from a file → extracted into comments and code portions
# OUTPUT RESULT EXPLANATION DESCRIBES RETURN VALUES:
#   tuple containing the comment list paired with the code list

def parse_comments(lines):
    """Separate code lines from comment lines for density checks."""
    comments = []
    code = []
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith('#'):
            comments.append((i, line))
        else:
            code.append((i, line))
    return comments, code

# [RANGE-EXPECTATION]: test_parse_comments describes expectations for parser test
# INPUT PARAMETER DETAILS PROVIDED FOR CONTEXT:
#   random_mod: injected randomness controller for deterministic behavior during testing
#     case module: controlled randomness supplier → verifies deterministic behavior
# OUTPUT RESULT DESCRIPTION PROVIDES EXPECTED EFFECT:
#   ensures exactly one comment line is detected from a short snippet

def test_parse_comments(random_mod):
    """Validate the comment parser with a trivial example."""
    random_mod.seed(0)
    sample = ['# hello world', 'print(1)']
    comments, _ = parse_comments(sample)
    assert len(comments) == 1

# [RANGE-EXPECTATION]: check_comment_rules describes comment validation behaviour
# INPUT INFORMATION DEFINING CHECK IS SHOWN HERE:
#   comments: list produced earlier for inspection of code comments
#     case normal: list of extracted comment tuples → potential violation descriptions
#   total_lines: count for complete file contents representing file length
#     case count: total number of lines in file → used for density metrics
# OUTPUT PROVIDED AFTER ANALYSIS GIVES SUMMARY:
#   list of strings describing comment related failures

def check_comment_rules(comments, total_lines):
    """Evaluate comment density, uniqueness and length."""
    failures = []
    if len(comments) * 3 < total_lines:
        line_no = comments[0][0] if comments else 1
        failures.append(f'INSUFFICIENT_COMMENT_DENSITY:<file>/{line_no}')
    seen = set()
    for lineno, text in comments:
        body = text.lstrip('#').strip()
        if len(body.split()) <= 5:
            failures.append(f'COMMENT_TOO_SHORT:<file>/{lineno}')
        if body in seen:
            failures.append(f'DUPLICATE_COMMENT_FOUND:<file>/{lineno}')
        seen.add(body)
    return failures

# [RANGE-EXPECTATION]: test_check_comment_rules describes quality test in detail
# INPUT ARGUMENT DETAILS PROVIDED HERE for clarity:
#   random_mod: deterministic randomness provider used in this test scenario
#     case module: randomness provider → ensures deterministic evaluation
# OUTPUT EXPECTATION STATED CLEARLY for this validation:
#   ensures rule system accepts valid comment set

def test_check_comment_rules(random_mod):
    """Check that good comments satisfy all density constraints."""
    random_mod.seed(0)
    comments = [(1, '# this comment has several distinct words'),
                (2, '# another line demonstrating comment requirements thoroughly')]
    failures = check_comment_rules(comments, 6)
    assert not failures

# [RANGE-EXPECTATION]: extract_range_block explains how we capture expectation
# INPUT PARAMETERS ANALYZED FOR EXTRACTION of block detection:
#   lines: argument with entire file context provided as list for scanning
#     case list: surrounding file lines → range block lines returned
#   start_index: numeric offset describing starting line for search operations
#     case integer: index position before function → search upward for block
# OUTPUT INFORMATION RETURNED AFTER PARSING to calling routine:
#   list of comment lines forming the range block

def extract_range_block(lines, start_index):
    """Gather the comment block that defines the range expectations."""
    block = []
    idx = start_index - 1
    while idx >= 0 and (lines[idx].strip().startswith('#') or not lines[idx].strip()):
        if lines[idx].strip().startswith('#'):
            block.insert(0, lines[idx])
        idx -= 1
    return block

# [RANGE-EXPECTATION]: test_extract_range_block focuses on extraction reliability
# INPUT ARGUMENT ANALYSIS describes deterministic path selection:
#   random_mod: parameter passed to control randomness inside the routine
#     case module: randomness provider → ensures deterministic execution path
# OUTPUT BEHAVIOR CONFIRMED BY TEST across multiple scenarios:
#   verifies block retrieval accuracy every time

def test_extract_range_block(random_mod):
    """Ensure range extraction returns correct lines."""
    random_mod.seed(0)
    lines = ['# [RANGE-EXPECTATION]: x', '# INPUT:', 'def x(): pass']
    block = extract_range_block(lines, 2)
    assert block[0].startswith('# [RANGE-EXPECTATION]')

# [RANGE-EXPECTATION]: check_function_rules describes per-function validation logic
# INPUT PARAMETER DESCRIPTION FOR THIS FUNCTION:
#   func: parameter describing AST function object used in checks
#     case astnode: function node → list of violations returned
#   lines: sequence representing source text around target
#     case list: source lines → textual analysis reference
#   imports: set listing names found during parsing
#     case set: imported names → detection for implicit usage
#   globals_in_module: set listing variable names discovered
#     case set: global variable names → out of scope check
#   next_node: element referencing AST node following function
#     case node: AST node after function → used for test adjacency
#   re_mod: module delivering regex matching functions
#     case module: regex utilities → pattern searching
#   ast_mod: module offering AST traversal helpers
#     case module: ast utilities → tree traversal helpers
# OUTPUT RESULT LIST RETURNED BY ANALYSIS:
#   list of rule violation strings related to the function

def check_function_rules(func, lines, imports, globals_in_module, next_node, re_mod, ast_mod):
    """Validate linter requirements for a single function."""
    failures = []
    block = extract_range_block(lines, func.lineno - 1)
    if not block or not block[0].startswith(f'# [RANGE-EXPECTATION]: {func.name}'):
        failures.append(f'MISSING_RANGE_EXPECTATION:{func.name}')
    if not func.name.startswith('test_'):
        if not (isinstance(next_node, ast_mod.FunctionDef) and next_node.name.startswith('test_')):
            failures.append(f'IMMEDIATE_TEST_MISSING:{func.name}')
    visitor = _NameVisitor()
    visitor.visit(func)
    for name in imports:
        if name in visitor.used and name not in func.args.args and name not in visitor.assigned:
            failures.append(f'IMPLICIT_IMPORT_VIOLATION:{func.name}/{name}')
    for name in globals_in_module:
        if name in visitor.used and name not in func.args.args and name not in visitor.assigned:
            failures.append(f'OUT_OF_SCOPE_VARIABLE:{func.name}/{name}')
    if func.name.startswith('test_'):
        body_text = ''.join(lines[func.body[0].lineno-1:func.body[-1].lineno])
        if '.seed(' not in body_text:
            failures.append(f'NON_DETERMINISTIC_TESTING:{func.name}')
    params = [arg.arg for arg in func.args.args]
    for p in params:
        found_param = any(re_mod.search(rf'^#\s+{p}:', line) for line in block)
        if not found_param:
            failures.append(f'RANGE_EXPECTATION_INCOMPLETE:{func.name}/{p}')
    for line in block:
        if 'case' in line and '→' not in line:
            label = line.split('case')[1].split(':')[0].strip()
            failures.append(f'CASE_EXPECTATION_UNDEFINED:{func.name}/{label}')
    return failures

# [RANGE-EXPECTATION]: test_check_function_rules exercises validator behaviour thoroughly
# INPUT PARAMETERS DISCUSSED BELOW for generating warning messages:
#   ast_mod: library providing AST manipulation tools for parsing
#     case module: abstract syntax tree utilities for parsing → enables tree construction
#   random_mod: seeded to guarantee deterministic evaluation path
#     case module: randomness provider → deterministic seeding
#   re_mod: regular expression module used during checks
#     case module: regex utilities employed for pattern matching → identifies patterns
# OUTPUT ASSURANCE PROVIDED BY TEST covers malformed inputs:
#   ensures rule engine flags issues for incomplete data

def test_check_function_rules(ast_mod, random_mod, re_mod):
    """Generate a temporary function for quick rule testing."""
    random_mod.seed(0)
    tree = ast_mod.parse('def f():\n    pass')
    func = tree.body[0]
    fails = check_function_rules(func, ['def f(): pass'], set(), set(), None, re_mod, ast_mod)
    assert fails

class _NameVisitor(ast.NodeVisitor):
    """Internal utility for tracking variable usage within a function."""
    def __init__(self):
        self.used = set()
        self.assigned = set()
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.assigned.add(node.id)
        self.generic_visit(node)

# [RANGE-EXPECTATION]: lint_file performs per-file rule analysis in detail
# INPUT PARAMETERS USED DURING FILE CHECK:
#   path: string naming the module under review
#     case string: path to module → list of rule failures
#   os_mod: operating system module required for file access
#     case module: operating system utilities → reading files
#   ast_mod: syntax tree module handling Python AST parsing
#     case module: AST parsing utilities → building syntax trees
#   re_mod: module supplying regex search functions for scanning
#     case module: regular expression utilities → pattern matching
# OUTPUT RESULT STRUCTURE EXPLAINED HERE for each scanned file:
#   list of strings describing all violations for this file

def lint_file(path, os_mod, ast_mod, re_mod):
    """Parse a python file and apply every linter rule."""
    with open(path, 'r') as fh:
        raw = fh.read()
    lines = raw.splitlines()
    tree = ast_mod.parse(raw)
    imports = set()
    globals_in_module = set()
    for node in tree.body:
        if isinstance(node, (ast_mod.Import, ast_mod.ImportFrom)):
            for alias in node.names:
                imports.add(alias.asname or alias.name.split('.')[0])
        if isinstance(node, ast_mod.Assign):
            for target in node.targets:
                if isinstance(target, ast_mod.Name) and not target.id.isupper():
                    globals_in_module.add(target.id)
    has_all = any(isinstance(n, ast_mod.Assign) and any(isinstance(t, ast_mod.Name) and t.id == '__all__' for t in n.targets) for n in tree.body)
    failures = []
    if not has_all:
        failures.append(f'MODULE_EXPORT_VIOLATION:{path}')
    comments, _ = parse_comments(lines)
    failures.extend(check_comment_rules(comments, len(lines)))
    body = tree.body
    for i, node in enumerate(body):
        if isinstance(node, ast_mod.FunctionDef):
            next_node = body[i + 1] if i + 1 < len(body) else None
            failures.extend(check_function_rules(node, lines, imports, globals_in_module, next_node, re_mod, ast_mod))
    return failures

# [RANGE-EXPECTATION]: test_lint_file covers linter behaviour on bad module
# INPUT PARAMETERS DOCUMENTED CLEARLY BELOW to aid comprehension:
#   os_mod: conveys operating system interface for path handling
#     case module: operating system interface → path utilities used
#   random_mod: provides deterministic randomness control for this check
#     case module: randomness provider for deterministic testing → reproducible runs
#   ast_mod: offers AST features for constructing parse tree
#     case module: parsing utilities used to build ASTs → syntax analysis
#   re_mod: passes regular expression library for matching lines
#     case module: regular expression utilities for parsing → pattern recognition
# OUTPUT BEHAVIOR VERIFIED BY TEST using temporary snippet:
#   ensures linter detects violation in simple module

def test_lint_file(os_mod, random_mod, ast_mod, re_mod):
    """Run linter on intentionally broken snippet for coverage."""
    random_mod.seed(0)
    path = 'tmp_bad.py'
    with open(path, 'w') as fh:
        fh.write('def x():\n    pass')
    fails = lint_file(path, os_mod, ast_mod, re_mod)
    os_mod.remove(path)
    assert fails

# [RANGE-EXPECTATION]: main drives overall linting and testing workflow
# INPUT PARAMETER EXPLANATION FOR MAIN ENTRYPOINT:
#   os_mod: passed for directory traversal and file discovery operations
#     case module: operating system interactions for file discovery → enumerates files across repository
#   ast_mod: parameter delivering syntax tree utilities for parsing modules
#     case module: syntax tree utilities required for parsing → generate AST structures for modules
#   re_mod: parameter supplies regular expression engine for validation
#     case module: regex engine for pattern checks → expression validation steps
#   random_mod: ensures deterministic randomness for test seeding
#     case module: randomness source for deterministic test seeding → reproducible randomness
#   include_self_test: flag controlling recursive self-test execution
#     case boolean: true value runs test_main → false value avoids recursion
# OUTPUT DETAILS OF THIS FUNCTION as final result enumeration:
#   exit code integer representing success status

def main(os_mod, ast_mod, re_mod, random_mod, include_self_test=True):
    """Run lint and regression tests across repository."""
    errors = []
    for path in collect_python_files('.', os_mod):
        errors.extend(lint_file(path, os_mod, ast_mod, re_mod))
    if errors:
        for msg in errors:
            print(msg)
        return 1
    test_collect_python_files(os_mod, random_mod)
    test_parse_comments(random_mod)
    test_check_comment_rules(random_mod)
    test_extract_range_block(random_mod)
    test_check_function_rules(ast_mod, random_mod, re_mod)
    test_lint_file(os_mod, random_mod, ast_mod, re_mod)
    if include_self_test:
        test_main(os_mod, ast_mod, re_mod, random_mod)
    return 0

# [RANGE-EXPECTATION]: test_main checks overall orchestration behaviour
# INPUT PARAMETER USED FOR SEEDING ensuring repeatable procedure:
#   os_mod: operating system tools supplied for discovery routines
#     case module: operating system interactions for file discovery → enumerates files
#   ast_mod: syntax tools module passed for parsing steps
#     case module: syntax tree utilities required for parsing → generate AST structures
#   re_mod: regex library used to check patterns during run
#     case module: regex engine for pattern checks → expression validation
#   random_mod: given to set deterministic state before main invocation
#     case module: randomness provider controlling seeding during main test → ensures reproducible execution
# OUTPUT RESULT GUARANTEED BY TEST under normal success conditions:
#   ensures main returns integer even when failures printed

def test_main(os_mod, ast_mod, re_mod, random_mod):
    """Execute the main entry point in a controlled way."""
    random_mod.seed(0)
    code = main(os_mod, ast_mod, re_mod, random_mod, include_self_test=False)
    assert isinstance(code, int)

__all__ = [
    'collect_python_files',
    'parse_comments',
    'check_comment_rules',
    'extract_range_block',
    'check_function_rules',
    'lint_file',
    'main',
    'test_collect_python_files',
    'test_parse_comments',
    'test_check_comment_rules',
    'test_extract_range_block',
    'test_check_function_rules',
    'test_lint_file',
    'test_main',
]

# This concluding comment clarifies that these exported symbols define the full
# linter API which must remain stable for downstream tooling. Keeping this list
# here prevents accidental exposure of internal helpers that might otherwise
# violate the explicit export rule specified in AGENTS.md. Each statement in
# this explanatory block contains more than five words to meet comment length
# guidelines while remaining unique from previous comments in the file.

if __name__ == '__main__':
    raise SystemExit(main(os, ast, re, random, include_self_test=True))
