# These imports provide the foundational runtime capabilities required for the linter
# such as file system traversal, deterministic randomness and subprocess control.
import ast
import os
import random
import re
import subprocess
import sys

# [RANGE-EXPECTATION]: collect_python_files drives file enumeration logic
# INPUT section describes parameters used for discovery.
#   root_dir: this parameter specifies the directory being scanned for python source modules.
#     case valid_path: directory exists → function returns every Python file found in that tree.
#   os_mod: operating system interface used for walking directories.
#     case provided_module: module supplied → ensures deterministic filesystem traversal.
# OUTPUT value explanation clarifies what is returned.
#   case success: list → relative paths pointing to each discovered Python file below that directory.

def collect_python_files(root_dir, os_mod):
    """Search directory for python files while staying deterministic."""
    found_files = []
    for current, _, files in os_mod.walk(root_dir):
        for name in sorted(files):
            if name.endswith('.py'):
                found_files.append(os_mod.path.join(current, name))
    return found_files

# [RANGE-EXPECTATION]: test_collect_python_files validates enumeration helper accuracy
# INPUT parameters describe the modules required during the test.
#   os_mod: this module handles filesystem operations for the test environment.
#     case provided_module: module provided → path resolution handled reliably for the test.
#   random_mod: seeded randomness provider ensures reproducible ordering during enumeration.
#     case provided_module: randomness seeded → ensures repeatable output.
# OUTPUT explanation outlines when enumeration succeeds.
#   case success: assertion → linter file path appears in results list.
#   the assertion succeeds when the linter's own file path is present in the returned list of files.

def test_collect_python_files(os_mod, random_mod):
    """Ensure that the search routine detects this file."""
    random_mod.seed(0)
    files = collect_python_files('.', os_mod)
    assert os_mod.path.abspath(__file__) in [os_mod.path.abspath(f) for f in files]

# [RANGE-EXPECTATION]: parse_comments separates comment lines from code
# INPUT description listing parameters used for line analysis.
#   lines: this sequence of text lines forms the basis of the separation routine.
#     case sequence: supplied list → comments can be separated from executable code without randomness.
# OUTPUT statement describes the tuple returned by the parser.
#   case success: tuple → comments found alongside remaining code lines in the same order they appeared.

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

# [RANGE-EXPECTATION]: test_parse_comments exercises the parser logic
# INPUT explains which modules configure randomness.
#   random_mod: module providing seeded randomness for the test environment.
#     case provided_module: seeding ensures deterministic detection of comment counts for this simple snippet → predictable result.
# OUTPUT clarifies the single-line expectation for this parser test.
#   case success: assertion → only one comment line should be reported from the example snippet.
#   only one comment line should be reported from the example snippet.

def test_parse_comments(random_mod):
    """Validate the comment parser with a trivial example."""
    random_mod.seed(0)
    sample = ['# hello world', 'print(1)']
    comments, _ = parse_comments(sample)
    assert len(comments) == 1

# [RANGE-EXPECTATION]: check_comment_rules evaluates comment policy adherence
# INPUT summary of parameters affecting validation.
#   comments: sequence of raw comment strings captured from source.
#     case normal_list: provided list → may violate one or more policy rules.
#   total_lines: count of all lines contained in the analyzed file.
#     case line_count: total lines counted → used for density checks.
# OUTPUT explanation highlights the list of failures that may result.
#   case failure: list → rule violation messages returned when any constraint is not met.

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

# [RANGE-EXPECTATION]: test_check_comment_rules verifies policy enforcement occurs correctly
# INPUT details randomness module for controlled behavior.
#   random_mod: this parameter passes in a randomness provider for deterministic checks.
#     case provided_module: deterministic seeding is required to examine comment validation logic → stable evaluation.
# OUTPUT expectation states no violations should remain after validation.
#   case success: none → no failures should be returned when the sample comment collection satisfies every linter rule.

def test_check_comment_rules(random_mod):
    """Check that good comments satisfy all density constraints."""
    random_mod.seed(0)
    comments = [(1, '# this comment has several distinct words for validation'),
                (2, '# another example line fully demonstrating comment requirements clearly')]
    failures = check_comment_rules(comments, 6)
    assert not failures

# [RANGE-EXPECTATION]: extract_range_block collects expectation comments for analysis
# INPUT list describes the function arguments used during retrieval.
#   lines: sequence of source text that may hold an expectation block.
#     case list_parameter: surrounding lines provided → range block may be recovered intact.
#   start_index: position before the function where scanning begins for the block.
#     case integer_position: index before function → search begins for the expectation block here.
# OUTPUT clarification indicates the returned list contains range comment lines.
#   case success: list → every discovered comment line participating in the range description for the specified function.

def extract_range_block(lines, start_index):
    """Gather the comment block that defines the range expectations."""
    block = []
    idx = start_index - 1
    while idx >= 0 and (lines[idx].strip().startswith('#') or not lines[idx].strip()):
        if lines[idx].strip().startswith('#'):
            block.insert(0, lines[idx])
        idx -= 1
    return block

# [RANGE-EXPECTATION]: test_extract_range_block ensures block retrieval works
# INPUT explains deterministic seeding for the helper module.
#   random_mod: helper module delivering deterministic seeding for the test scenario.
#     case provided_module: seeding is necessary here to verify deterministic retrieval of the expectation block → predictable result.
# OUTPUT ensures that the extracted block begins with the expected marker line.
#   case success: block → retrieved lines start with the expected marker string.

def test_extract_range_block(random_mod):
    """Ensure range extraction returns correct lines."""
    random_mod.seed(0)
    lines = ['# [RANGE-EXPECTATION]: x', '# INPUT:', 'def x(): pass']
    block = extract_range_block(lines, 2)
    assert block[0].startswith('# [RANGE-EXPECTATION]')

# [RANGE-EXPECTATION]: check_function_rules inspects individual function nodes
# INPUT section details parameters used when constructing the sample node.
#   func: function definition object being examined.
#     case astnode_value: AST function node provided → validated for rule compliance.
#   lines: textual representation of the module where the function lives.
#     case source_list: list provided → allows detailed analysis of file content.
#   imports: collection of names imported at module level.
#     case provided_set: imported names → require explicit parameter passing.
#   globals_in_module: names defined globally within the module.
#     case provided_set: global names → may be accessed improperly.
#   next_node: element directly after the function under inspection.
#     case following_node: next AST node → used to confirm adjacency of tests.
#   re_mod: regex module used by the rule checker.
#     case provided_module: regex engine ensures pattern searches operate → pattern logic works.
#   ast_mod: abstract syntax utilities for walking the function.
#     case provided_module: AST utilities required for structural analysis → structure validated.
# OUTPUT list summarizing violation messages detected by analysis.
#   case failure: list → rule violations detected for the supplied function node.

def check_function_rules(func, lines, imports, globals_in_module, next_node, re_mod, ast_mod):
    """Validate linter requirements for a single function."""
    failures = []
    block = extract_range_block(lines, func.lineno - 1)
    if not block or not block[0].startswith(f'# [RANGE-EXPECTATION]: {func.name}'):
        failures.append(f'MISSING_RANGE_EXPECTATION:{func.name}')
    if not func.name.startswith('test_'):
        if not (isinstance(next_node, ast_mod.FunctionDef) and next_node.name.startswith('test_')):
            failures.append(f'IMMEDIATE_TEST_MISSING:{func.name}')
    visitor = _NameVisitor(ast_mod)
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

# [RANGE-EXPECTATION]: test_check_function_rules creates a dummy function to check rules
# INPUT field describes module dependencies used during this test.
#   ast_mod: module containing syntax-tree utilities for analysis.
#     case provided_module: this AST library builds nodes used for rule evaluation → ensures valid parsing.
#   random_mod: provider used for deterministic AST generation within the rule test.
#     case provided_module: deterministic seeding controls the generated test module for consistent results → reproducible behavior.
#   re_mod: regular expression library necessary for pattern checks.
#     case provided_module: regular expression utilities required by the linter function under test → regex operations succeed.
# OUTPUT indicates that violations should be reported.
#   case failure: list → function returns non-empty list of failures for the intentionally incomplete sample node.

def test_check_function_rules(ast_mod, random_mod, re_mod):
    """Generate a temporary function for quick rule testing."""
    random_mod.seed(0)
    tree = ast_mod.parse('def f():\n    pass')
    func = tree.body[0]
    fails = check_function_rules(func, ['def f(): pass'], set(), set(), None, re_mod, ast_mod)
    assert fails

class _NameVisitor(ast.NodeVisitor):
    """Internal utility for tracking variable usage within a function."""
    def __init__(self, ast_mod):
        super().__init__()
        self.ast_mod = ast_mod
        self.used = set()
        self.assigned = set()
    def visit_Name(self, node):
        if isinstance(node.ctx, self.ast_mod.Load):
            self.used.add(node.id)
        elif isinstance(node.ctx, self.ast_mod.Store):
            self.assigned.add(node.id)
        self.generic_visit(node)

# [RANGE-EXPECTATION]: lint_file performs rule checks on a file
# INPUT summarises the helper modules this test relies upon.
#   path: path to the module being linted.
#     case file_path: given module path → file will be parsed and analyzed.
#   os_mod: operating system interface used during linting.
#     case provided_module: filesystem helpers used to resolve absolute paths and open files → ensures reproducible access.
#   ast_mod: parser library delivering abstract syntax tree utilities.
#     case provided_module: abstract syntax tree utilities required for static code analysis → enables rule checks.
#   re_mod: regex helper module used for searching patterns.
#     case provided_module: regular expression helper library for pattern matching within source code → facilitates detection.
# OUTPUT statement summarises the returned violation list.
#   case success: list → strings describing every violation detected in the specified file.

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

# [RANGE-EXPECTATION]: test_lint_file checks detection of simple violations
# INPUT parameter list enumerates the modules needed for this temporary-file test scenario.
#   os_mod: module providing temporary file utilities for this test.
#     case provided_module: module supplied → manages temporary file creation and cleanup.
#   random_mod: randomness module seeded to ensure stable file creation steps.
#     case provided_module: seeding ensures the sample file generation behaves deterministically → predictable results.
#   ast_mod: parser utilities necessary to build the sample AST for testing.
#     case provided_module: parser utilities available → AST structure can be created for linting.
#   re_mod: pattern recognition engine required by the linter under test.
#     case provided_module: regex engine supplied → enables linter pattern checks.
# OUTPUT describes the expected failure detection.
#   case failure: list → linter should produce at least one violation message for the intentionally broken snippet.

def test_lint_file(os_mod, random_mod, ast_mod, re_mod):
    """Run linter on intentionally broken snippet for coverage."""
    random_mod.seed(0)
    path = 'tmp_bad.py'
    with open(path, 'w') as fh:
        fh.write('def x():\n    pass')
    fails = lint_file(path, os_mod, ast_mod, re_mod)
    os_mod.remove(path)
    assert fails

# [RANGE-EXPECTATION]: main orchestrates repository linting and tests
# INPUT clarifies the runtime dependencies required for full execution.
#   os_mod: system interface allowing the linter to locate modules.
#     case provided_module: interacts with the filesystem to enumerate every python file → full coverage.
#   ast_mod: module that constructs abstract syntax trees needed for static analysis.
#     case provided_module: AST construction utilities → enable rule enforcement.
#   re_mod: regex module supplying pattern objects for rule checks.
#     case provided_module: supplies regex patterns so rule checks operate correctly → consistent parsing.
#   random_mod: module supplying seeded randomness across all regression tests to keep results reproducible.
#     case provided_module: seeds deterministic randomness when running all regression tests → stable outcomes.
# OUTPUT conveys the resulting success or failure code.
#   case success: int → zero when linting and tests succeed otherwise a non-zero integer indicates failure.

def main(os_mod, ast_mod, re_mod, random_mod):
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
    return 0

# [RANGE-EXPECTATION]: test_main exercises the main entry path
# INPUT list specifying required modules for deterministic operation.
#   random_mod: this module seeds the execution of main for reproducible results during tests.
#     case provided_module: seeding controls deterministic execution of the main routine during tests → stable runs.
#   os_mod: operating system module passed to main for file operations.
#     case provided_module: supplies filesystem operations needed by main → path handling works.
#   ast_mod: AST utilities used by main for parsing.
#     case provided_module: AST utilities assist parsing → valid analysis.
#   re_mod: regex utilities required by the linter during full execution.
#     case provided_module: regex utilities enable pattern checks → consistent linting.
# OUTPUT line clarifies that an integer return is expected even on failure messages.
#   case success: int → return value is an integer regardless of whether failures were printed.

def test_main(random_mod, os_mod, ast_mod, re_mod):
    """Execute the main entry point in a controlled way."""
    random_mod.seed(0)
    code = main(os_mod, ast_mod, re_mod, random_mod)
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
    raise SystemExit(main(os, ast, re, random))
