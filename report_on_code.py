# report_on_code.py
import ast
import os
import json
import re
from typing import List, Dict, Tuple, Set

###############################
# Existing Analysis Functions #
###############################


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        # Mapping: imported name -> (line number, full import description)
        self.imports: Dict[str, Tuple[int, str]] = {}
        # Set of names that are actually used in the code
        self.used: Set[str] = set()


    def visit_ImportFrom(self, node: ast.ImportFrom):
        # Skip star imports since it's hard to track usage (e.g. "from module import *")
        if any(alias.name == "*" for alias in node.names):
            return

        for alias in node.names:
            # For "from module import name", get the alias if it exists
            imported_name = alias.asname if alias.asname else alias.name
            if node.module:
                full_import = f"{node.module}.{alias.name}"
            else:
                full_import = alias.name
            self.imports[imported_name] = (node.lineno, full_import)
        self.generic_visit(node)


    def visit_ImportFrom(self, node: ast.ImportFrom):
        # Skip star imports since it's hard to track usage (e.g. "from module import *")
        if any(alias.name == "*" for alias in node.names):
            return

        for alias in node.names:
            # For "from module import name", get the alias if it exists
            imported_name = alias.asname if alias.asname else alias.name
            full_import = f"{node.module}.{
                alias.name}" if node.module else alias.name
            self.imports[imported_name] = (node.lineno, full_import)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        # Record each occurrence of a name usage
        self.used.add(node.id)
        self.generic_visit(node)


def find_unused_imports(source_code: str) -> List[str]:
    """
    Analyzes the given Python source code and returns a list of strings
    describing the unused imports along with their line numbers.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    visitor = ImportVisitor()
    visitor.visit(tree)

    unused = []
    for imported_name, (lineno, full_import) in visitor.imports.items():
        if imported_name not in visitor.used:
            unused.append(f"Unused import '{full_import}' on line {lineno}")
    return unused


def compute_complexity(source_code: str) -> List[Tuple[str, int]]:
    """
    Computes a basic cyclomatic complexity for each function defined in the source code.
    The complexity is calculated as 1 (for the function itself) plus the number of decision points.
    Decision points include: if, for, while, and, or, try/except, etc.
    
    Returns:
        A list of tuples, each containing the function name and its computed complexity.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [("SyntaxError", 0)]

    complexities = []

    # A helper function to count decision points in a function body
    def count_decision_points(node: ast.AST) -> int:
        count = 0
        for child in ast.walk(node):
            # Each of these nodes adds one decision point.
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                count += 1
            # Boolean operators 'and' and 'or' can increase complexity.
            elif isinstance(child, ast.BoolOp) and isinstance(child.op, (ast.And, ast.Or)):
                # Each boolean operation can be considered as an extra decision point.
                count += len(child.values) - 1
        return count

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Base complexity is 1, plus decision points.
            complexity = 1 + count_decision_points(node)
            complexities.append((node.name, complexity))
    return complexities

# Now, update your check_complexity function to use our custom compute_complexity:


def check_complexity(source_code: str, threshold: int = 10) -> List[str]:
    """
    Checks the cyclomatic complexity of functions in the provided source code.
    Returns a list of warnings for functions exceeding the threshold.
    This version uses a custom complexity calculator implemented with built-in modules.
    """
    warnings = []
    complexity_results = compute_complexity(source_code)
    for func_name, complexity in complexity_results:
        if complexity > threshold:
            warnings.append(
                f"Function '{func_name}' has a complexity of {
                    complexity} (threshold: {threshold})."
            )
    return warnings



def validate_docstrings(source_code: str) -> List[str]:
    """
    Validates that each function and class in the source code has a docstring.
    Returns a list of warnings for missing docstrings.
    """
    warnings = []
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node) is None:
                warnings.append(
                    f"Missing docstring in {type(node).__name__} '{
                        node.name}' at line {node.lineno}."
                )
    return warnings


class UnusedVariableVisitor(ast.NodeVisitor):
    def __init__(self):
        self.assignments = {}
        self.usage = set()

    def visit_Assign(self, node: ast.Assign):
        # Capture targets of assignment (considering simple cases)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assignments[target.id] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            self.usage.add(node.id)
        self.generic_visit(node)


def find_unused_variables(source_code: str) -> List[str]:
    """
    Analyzes the source code and returns warnings for variables that are assigned but never used.
    """
    tree = ast.parse(source_code)
    visitor = UnusedVariableVisitor()
    visitor.visit(tree)
    unused_vars = []
    for var, lineno in visitor.assignments.items():
        if var not in visitor.usage:
            unused_vars.append(f"Variable '{var}' assigned at line {
                               lineno} is never used.")
    return unused_vars

####################################
# Additional Built-in Checkers     #
####################################


def check_naming_conventions(source_code: str) -> List[str]:
    """
    Checks that function names are snake_case and class names are CamelCase.
    Returns warnings if naming conventions are not followed.
    """
    warnings = []
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Simple regex for snake_case (lowercase, numbers, underscores)
            if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                warnings.append(f"Function '{node.name}' at line {
                                node.lineno} should be snake_case.")
        elif isinstance(node, ast.ClassDef):
            # Simple regex for CamelCase (starting with uppercase, no underscores)
            if not re.match(r'^[A-Z][a-zA-Z0-9]+$', node.name):
                warnings.append(f"Class '{node.name}' at line {
                                node.lineno} should be CamelCase.")
    return warnings


def check_trailing_whitespace(file_path: str) -> List[str]:
    """
    Reads the file and checks for trailing whitespace on any line.
    Returns a list of warnings indicating line numbers with trailing whitespace.
    """
    warnings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if line.rstrip("\n") != line.rstrip():
                    warnings.append(f"Line {i} has trailing whitespace.")
    except Exception as e:
        warnings.append(f"Error reading file: {e}")
    return warnings


def check_line_length(file_path: str, max_length: int = 80) -> List[str]:
    """
    Checks that no line in the file exceeds the max_length.
    Returns warnings for each line that exceeds the limit.
    """
    warnings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if len(line.rstrip("\n")) > max_length:
                    warnings.append(f"Line {i} exceeds {
                                    max_length} characters.")
    except Exception as e:
        warnings.append(f"Error reading file: {e}")
    return warnings


def check_import_order(file_path: str) -> List[str]:
    """
    Checks that top-level import statements in the file are sorted alphabetically.
    Returns warnings if the imports are not in sorted order.
    """
    warnings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return [f"Error reading file: {e}"]

    # Collect top-level import lines (ignoring indented imports)
    import_lines = []
    for line in lines:
        stripped = line.lstrip()
        # Only consider lines that start with 'import' or 'from' without indentation
        if (stripped.startswith("import ") or stripped.startswith("from ")) and line[0] not in (" ", "\t"):
            import_lines.append(stripped.strip())

    # Check if the list of import lines is already sorted (case-insensitive)
    if import_lines and import_lines != sorted(import_lines, key=lambda s: s.lower()):
        warnings.append(
            "Top-level import statements are not sorted alphabetically.")
    return warnings


def check_function_length(source_code: str, max_lines: int = 50) -> List[str]:
    """
    Checks if any function in the provided source code exceeds a specified number of lines.
    Returns warnings for functions that are too long.
    
    Parameters:
        source_code (str): The Python source code to analyze.
        max_lines (int): The maximum acceptable number of lines for a function.
        
    Returns:
        List[str]: A list of warning messages for functions exceeding the maximum length.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Using Python 3.8+ where end_lineno is available.
            if hasattr(node, "end_lineno") and node.end_lineno is not None:
                function_length = node.end_lineno - node.lineno + 1
            else:
                # Fallback: use the last statement's line number if end_lineno is not available.
                function_length = node.body[-1].lineno - \
                    node.lineno + 1 if node.body else 0

            if function_length > max_lines:
                end_line = node.end_lineno if hasattr(
                    node, "end_lineno") else "unknown"
                warnings.append(
                    f"Function '{node.name}' (lines {
                        node.lineno}-{end_line}) is too long ({function_length} lines; max is {max_lines})."
                )
    return warnings


def check_todo_comments(file_path: str) -> List[str]:
    """
    Checks for 'TODO' or 'FIXME' comments in the file and returns warnings with their line numbers.
    
    Parameters:
        file_path (str): The path to the file to check.
        
    Returns:
        List[str]: A list of warning messages for each line containing a TODO or FIXME comment.
    """
    warnings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if "TODO" in line or "FIXME" in line:
                    warnings.append(
                        f"Line {i} contains a TODO/FIXME comment: {line.strip()}")
    except Exception as e:
        warnings.append(f"Error reading file: {e}")
    return warnings


def check_main_guard(source_code: str) -> List[str]:
    """
    Checks if the source code contains the '__main__' guard.
    Returns a warning if it's missing.
    """
    warnings = []
    if '__main__' not in source_code:
        warnings.append("No '__main__' guard found in the file.")
    return warnings


def check_unused_function_parameters(source_code: str) -> List[str]:
    """
    Analyzes functions to find parameters that are never used in their body.
    Returns warnings for each unused parameter.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Get all parameter names
            params = {arg.arg for arg in node.args.args}
            # Get all names used in the function body
            used_names = {n.id for n in ast.walk(
                node) if isinstance(n, ast.Name)}
            unused_params = params - used_names
            for param in unused_params:
                warnings.append(
                    f"Function '{node.name}' at line {
                        node.lineno} has an unused parameter: '{param}'."
                )
    return warnings


def check_missing_type_hints(source_code: str) -> List[str]:
    """
    Checks for functions missing type hints for parameters or return values.
    Returns warnings for each function that lacks type annotations.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            missing_params = [
                arg.arg for arg in node.args.args if arg.annotation is None]
            missing_return = node.returns is None
            if missing_params or missing_return:
                message = f"Function '{node.name}' at line {
                    node.lineno} is missing type hints"
                if missing_params:
                    message += f" for parameters: {', '.join(missing_params)}"
                if missing_return:
                    message += " and a return type."
                warnings.append(message)
    return warnings


def check_global_variables(source_code: str) -> List[str]:
    """
    Checks for global variable assignments at the module level.
    Returns warnings for each global variable found.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    # In the module-level, any Assign node not nested in a function or class is a global.
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            for var in targets:
                warnings.append(f"Global variable '{
                                var}' assigned at line {node.lineno}.")
    return warnings


class NestingVisitor(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def generic_visit(self, node):
        # Increase nesting for nodes that introduce a block.
        if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            super().generic_visit(node)
            self.current_depth -= 1
        else:
            super().generic_visit(node)


def check_excessive_nesting(source_code: str, max_depth: int = 4) -> List[str]:
    """
    Checks if any function exceeds the allowed nesting depth.
    Returns warnings if a function's nesting depth exceeds max_depth.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            visitor = NestingVisitor()
            visitor.visit(node)
            if visitor.max_depth > max_depth:
                warnings.append(
                    f"Function '{node.name}' at line {node.lineno} has excessive nesting (depth {
                        visitor.max_depth}; max allowed is {max_depth})."
                )
    return warnings


def build_dependency_graph(directory: str) -> Dict[str, Set[str]]:
    """
    Walks through the directory and builds a graph where keys are module names
    (derived from file names without extension) and values are sets of module names
    that are imported.
    """
    graph = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                module_name = os.path.splitext(file)[0]
                graph[module_name] = set()
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()
                    tree = ast.parse(source)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imported = alias.name.split('.')[0]
                                graph[module_name].add(imported)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imported = node.module.split('.')[0]
                                graph[module_name].add(imported)
                except Exception:
                    continue
    return graph


def detect_cycles(graph: Dict[str, Set[str]]) -> List[str]:
    """
    Detects cycles in the dependency graph. Returns a list of warnings describing
    the cycles found.
    """
    warnings = []
    visited = set()
    rec_stack = set()

    def visit(node, path):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                cycle = visit(neighbor, path + [neighbor])
                if cycle:
                    return cycle
            elif neighbor in rec_stack:
                # Cycle found; return the cycle path.
                cycle_start_index = path.index(
                    neighbor) if neighbor in path else 0
                return path[cycle_start_index:] + [neighbor]
        rec_stack.remove(node)
        return None

    for mod in graph:
        if mod not in visited:
            cycle = visit(mod, [mod])
            if cycle:
                warnings.append(
                    "Circular dependency detected: " + " -> ".join(cycle))
    return warnings


def check_circular_dependencies(directory: str) -> List[str]:
    """
    Checks the entire directory for circular dependencies between modules.
    Returns warnings if cycles are detected.
    """
    graph = build_dependency_graph(directory)
    return detect_cycles(graph)


def detect_magic_numbers(source_code: str, allowed: Set[float] = {0, 1}) -> List[str]:
    """
    Scans the source code for numeric literals (magic numbers) that are not in the allowed set.
    Returns warnings for each occurrence.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    class MagicNumberVisitor(ast.NodeVisitor):
        def visit_Constant(self, node):
            if isinstance(node.value, (int, float)) and node.value not in allowed:
                warnings.append(
                    f"Magic number {node.value} found at line {node.lineno}.")
        # For Python versions <3.8, use Num:

        def visit_Num(self, node):
            if node.n not in allowed:
                warnings.append(
                    f"Magic number {node.n} found at line {node.lineno}.")

    MagicNumberVisitor().visit(tree)
    return warnings


def find_duplicate_functions(source_code: str) -> List[str]:
    """
    Extracts function definitions and checks for duplicate function bodies.
    Returns warnings if duplicate functions (by body) are found.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    func_bodies = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Normalize the function body by converting it to unparsed code
            # Here we simply join the line numbers for a crude fingerprint.
            body_fingerprint = " ".join(str(n.lineno)
                                        for n in node.body if hasattr(n, "lineno"))
            if body_fingerprint in func_bodies:
                warnings.append(
                    f"Duplicate function body found in '{
                        node.name}' at line {node.lineno} and "
                    f"'{func_bodies[body_fingerprint]}'"
                )
            else:
                func_bodies[body_fingerprint] = node.name
    return warnings


def check_exception_logging(source_code: str) -> List[str]:
    """
    Checks that every except block in the code includes a logging or print statement.
    Returns warnings for except blocks that might be missing proper logging.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                found_logging = False
                for n in ast.walk(handler):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                        if n.func.id in {"print", "log", "logger", "logging"}:
                            found_logging = True
                            break
                if not found_logging:
                    warnings.append(
                        f"Except block at line {
                            handler.lineno} might be missing logging/print calls."
                    )
    return warnings


def check_logging_in_exceptions(source_code: str) -> List[str]:
    """
    Checks that every try/except block in the source code contains a call to a logging function.
    Returns warnings for each try/except block that might be missing logging.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    expected_log_calls = {"print", "log", "logger", "logging"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                has_log = False
                for n in ast.walk(handler):
                    if isinstance(n, ast.Call):
                        if isinstance(n.func, ast.Name) and n.func.id in expected_log_calls:
                            has_log = True
                        elif isinstance(n.func, ast.Attribute) and n.func.attr in expected_log_calls:
                            has_log = True
                    if has_log:
                        break
                if not has_log:
                    warnings.append(
                        f"Try/except block at line {
                            handler.lineno} may not log exceptions properly."
                    )
    return warnings


def check_deprecated_usage(source_code: str, deprecated: Set[str]) -> List[str]:
    """
    Checks the source code for usage of deprecated APIs.
    'deprecated' is a set of deprecated function or method names.
    Returns warnings for each usage found.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in deprecated:
                warnings.append(f"Deprecated API '{
                                node.func.id}' used at line {node.lineno}.")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            # Check for method calls like module.deprecated_function(...)
            if node.func.attr in deprecated:
                warnings.append(f"Deprecated API '{
                                node.func.attr}' used at line {node.lineno}.")
    return warnings


def check_test_coverage(source_directory: str, test_directory: str = "tests") -> List[str]:
    """
    Checks that for each Python file in the source directory (excluding __init__.py and files in the test directory)
    there is a corresponding test file in the test_directory (named 'test_<module>.py').
    Returns warnings for any modules missing tests.
    """
    warnings = []
    source_files = []
    for root, _, files in os.walk(source_directory):
        # Skip test_directory
        if test_directory in root:
            continue
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                source_files.append(os.path.splitext(file)[0])

    test_files = set()
    for root, _, files in os.walk(test_directory):
        for file in files:
            if file.endswith(".py"):
                # Assume test files are named as test_<module>.py
                if file.startswith("test_"):
                    test_files.add(file[5:-3])  # extract <module>

    for module in source_files:
        if module not in test_files:
            warnings.append(f"Module '{module}.py' is missing a corresponding test file in '{
                            test_directory}'.")
    return warnings


def check_commented_out_code(file_path: str) -> List[str]:
    """
    Scans the file for lines that appear to be commented-out code.
    Returns warnings for each suspicious commented line.
    """
    warnings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                # If a comment contains code-like patterns (e.g., "def", "class", or an assignment)
                if stripped.startswith("#") and (("def " in stripped) or ("class " in stripped) or ("=" in stripped)):
                    warnings.append(
                        f"Line {i} appears to be commented-out code: {stripped}")
    except Exception as e:
        warnings.append(f"Error reading file: {e}")
    return warnings


def check_file_length(file_path: str, max_lines: int = 500) -> List[str]:
    """
    Checks if the file exceeds the maximum allowed number of lines.
    Returns warnings if the file is too long.
    """
    warnings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            warnings.append(
                f"File has {len(lines)} lines, which exceeds the max allowed {max_lines}.")
    except Exception as e:
        warnings.append(f"Error reading file: {e}")
    return warnings


def check_excessive_lambda_usage(source_code: str, max_expr_length: int = 30) -> List[str]:
    """
    Checks for lambda expressions that are excessively long or complex.
    Returns warnings if a lambda's source code exceeds a given character length.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Lambda):
            # Use ast.get_source_segment if available (Python 3.8+), or a fallback
            lambda_source = ast.get_source_segment(source_code, node)
            if lambda_source and len(lambda_source) > max_expr_length:
                warnings.append(f"Lambda expression at line {
                                node.lineno} is too long: {lambda_source}")
    return warnings


def check_dangerous_functions(source_code: str) -> List[str]:
    """
    Checks the source code for the usage of dangerous functions like eval or exec.
    Returns warnings for each occurrence.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                warnings.append(f"Dangerous function '{
                                node.func.id}' used at line {node.lineno}.")
    return warnings


def check_builtin_shadowing(source_code: str) -> List[str]:
    """
    Checks the source code for identifiers that shadow Python built-in names.
    Returns warnings for each occurrence.
    """
    warnings = []
    # Get a set of Python built-in names
    builtins_set = set(dir(__import__('builtins')))
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        # Check function parameters
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg in builtins_set:
                    warnings.append(
                        f"In function '{node.name}' at line {node.lineno}: parameter '{
                            arg.arg}' shadows a built-in name."
                    )
        # Check assignments that create variables
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in builtins_set:
                    warnings.append(
                        f"Variable '{target.id}' assigned at line {
                            node.lineno} shadows a built-in name."
                    )
    return warnings


def check_mixed_indentation(file_path: str) -> List[str]:
    """
    Checks the file for mixed indentation (tabs and spaces).
    Returns warnings if both types are found.
    """
    warnings = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return [f"Error reading file: {e}"]

    found_tabs = False
    found_spaces = False
    for line in lines:
        # Ignore empty lines
        if line.strip() == "":
            continue
        if line.startswith("\t"):
            found_tabs = True
        elif line.startswith(" "):
            found_spaces = True
        if found_tabs and found_spaces:
            warnings.append("Mixed indentation detected (tabs and spaces).")
            break
    return warnings


def check_module_docstring(source_code: str) -> List[str]:
    """
    Checks if the module has a top-level docstring.
    Returns a warning if the docstring is missing.
    """
    warnings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    # The module docstring is expected to be the first statement in the module.
    if not tree.body or not isinstance(tree.body[0], ast.Expr) or not isinstance(tree.body[0].value, (ast.Str, ast.Constant)):
        warnings.append("Module is missing a top-level docstring.")
    return warnings


####################################
# File and Directory Analysis      #
####################################


def analyze_file(file_path: str, complexity_threshold: int = 10) -> Dict[str, List[str]]:
    """
    Analyzes a single Python file for various quality issues.
    Returns a dictionary of warnings.
    """
    warnings = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
    except Exception as e:
        return {"error": [f"Error reading file: {e}"]}

    warnings["unused_imports"] = find_unused_imports(source_code)
    warnings["complexity_warnings"] = check_complexity(
        source_code, threshold=complexity_threshold)
    warnings["docstring_warnings"] = validate_docstrings(source_code)
    warnings["unused_variables"] = find_unused_variables(source_code)
    warnings["naming_warnings"] = check_naming_conventions(source_code)
    # For whitespace and line length, pass file_path directly
    warnings["trailing_whitespace"] = check_trailing_whitespace(file_path)
    warnings["line_length_warnings"] = check_line_length(
        file_path, max_length=80)
    warnings["import_order_warnings"] = check_import_order(file_path)
    warnings["function_length_warnings"] = check_function_length(source_code)
    warnings["todo_comments_warnings"] = check_todo_comments(file_path)
    warnings["global_variables"] = check_global_variables(source_code)


    warnings["excessive_nesting"] = check_excessive_nesting(source_code)
    warnings["main_guard"] = check_main_guard(source_code)
    warnings["unused_parameters"] = check_unused_function_parameters(source_code)
    warnings["missing_type_hints"] = check_missing_type_hints(source_code)

    warnings["circular_dependencies"] = check_circular_dependencies(
        os.path.dirname(file_path))
    warnings["magic_numbers"] = detect_magic_numbers(source_code)
    warnings["duplicate_functions"] = find_duplicate_functions(source_code)
    warnings["exception_logging"] = check_exception_logging(source_code)
    warnings["logging_in_exceptions"] = check_logging_in_exceptions(
        source_code)
    warnings["deprecated_usage"] = check_deprecated_usage(
        source_code, deprecated={"old_func", "legacy_method"})
    warnings["test_coverage"] = check_test_coverage(os.path.dirname(file_path))

    warnings["dangerous_functions"] = check_dangerous_functions(source_code)
    warnings["commented_out_code"] = check_commented_out_code(file_path)
    warnings["file_length"] = check_file_length(file_path, max_lines=500)
    warnings["excessive_lambda_usage"] = check_excessive_lambda_usage(
        source_code)
    warnings["module_docstring"] = check_module_docstring(source_code)
    warnings["mixed_indentation"] = check_mixed_indentation(file_path)
    warnings["builtin_shadowing"] = check_builtin_shadowing(source_code)

    return warnings


def analyze_directory(directory: str, complexity_threshold: int = 10) -> Dict[str, Dict[str, List[str]]]:
    """
    Walks through the directory, analyzes all .py files, and returns a dictionary
    where keys are file paths and values are dictionaries of warnings.
    """
    results = {}
    for root, dirs, files in os.walk(directory):
        # Remove 'venv' directory from dirs to prevent os.walk from traversing it.
        if 'venv' in dirs:
            dirs.remove('venv')
            dirs.remove('pyds')
            dirs.remove('gen_ai')
            dirs.remove('gen_ai_code')
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                results[file_path] = analyze_file(
                    file_path, complexity_threshold)
    return results


def analyze_code_metrics(source_code: str) -> Dict[str, float]:
    """
    Computes basic code metrics from the source code:
      - total lines
      - non-blank, non-comment code lines
      - comment lines
      - blank lines
      - number of functions and classes
      - comment-to-code ratio

    Returns:
        A dictionary with these metrics.
    """
    lines = source_code.splitlines()
    total_lines = len(lines)
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    blank_lines = sum(1 for line in lines if line.strip() == "")
    code_lines = total_lines - comment_lines - blank_lines

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        # If parsing fails, simply set counts to 0
        function_count = 0
        class_count = 0
    else:
        function_count = sum(1 for node in ast.walk(
            tree) if isinstance(node, ast.FunctionDef))
        class_count = sum(1 for node in ast.walk(
            tree) if isinstance(node, ast.ClassDef))

    metrics = {
        "total_lines": total_lines,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "blank_lines": blank_lines,
        "function_count": function_count,
        "class_count": class_count,
        "comment_ratio": comment_lines / total_lines if total_lines > 0 else 0,
    }
    return metrics


def analyze_file_metrics(file_path: str, complexity_threshold: int = 10) -> Dict[str, any]:
    """
    Analyzes a single file and returns both quality warnings and code metrics.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
    except Exception as e:
        return {"error": f"Error reading file: {e}"}

    warnings = analyze_file(file_path, complexity_threshold)
    metrics = analyze_code_metrics(source_code)
    return {"warnings": warnings, "metrics": metrics}


def aggregate_code_metrics(directory: str) -> Dict[str, float]:
    """
    Walks through the directory and aggregates code metrics from each Python file.
    Returns a dictionary with overall totals and averages.
    """
    total_files = 0
    aggregate = {
        "total_lines": 0,
        "code_lines": 0,
        "comment_lines": 0,
        "blank_lines": 0,
        "function_count": 0,
        "class_count": 0,
    }

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                total_files += 1
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source_code = f.read()
                    metrics = analyze_code_metrics(source_code)
                    for key in aggregate:
                        aggregate[key] += metrics.get(key, 0)
                except Exception:
                    continue

    # Calculate averages where applicable
    averages = {}
    if total_files:
        for key, value in aggregate.items():
            averages[f"avg_{key}"] = value / total_files
    return {**aggregate, "total_files": total_files, **averages}


def summarize_warnings(results: Dict[str, Dict[str, List[str]]]) -> Dict[str, int]:
    """
    Summarizes the warnings across all analyzed files.
    Returns a dictionary where keys are warning categories and values are the total count.
    """
    summary = {}
    for file_warnings in results.values():
        for category, warnings in file_warnings.items():
            summary[category] = summary.get(category, 0) + len(warnings)
    return summary


def write_results_to_json(results: Dict[str, Dict[str, List[str]]], output_file: str):
    """
    Writes the results dictionary to a JSON file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)


####################################
# Example Usage                    #
####################################

def main():
    # Set the directory you want to analyze.
    directory_to_analyze = "."  # Change this as needed.

    # 1. Analyze all Python files in the directory for warnings.
    analysis_results = analyze_directory(
        directory_to_analyze, complexity_threshold=10)

    # Write the complete analysis results to a JSON file.
    output_json = "analysis_results.json"
    write_results_to_json(analysis_results, output_json)
    print(f"Full analysis complete. Results saved to {output_json}")

    # 2. Analyze metrics for a specific file.
    sample_file = os.path.join(directory_to_analyze, "example.py")
    file_report = analyze_file_metrics(sample_file, complexity_threshold=10)
    print(f"\nMetrics and warnings for {sample_file}:")
    print(json.dumps(file_report, indent=4))

    # 3. Aggregate code metrics for the entire directory.
    overall_metrics = aggregate_code_metrics(directory_to_analyze)
    print("\nAggregated code metrics for the directory:")
    print(json.dumps(overall_metrics, indent=4))

    # 4. Summarize warnings across the entire analysis.
    warnings_summary = summarize_warnings(analysis_results)
    print("\nWarnings summary (total count per category):")
    print(json.dumps(warnings_summary, indent=4))


if __name__ == "__main__":
    main()
