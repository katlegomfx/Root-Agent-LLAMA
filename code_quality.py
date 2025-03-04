# code_quality.py
import ast
import json
import os


def find_unused_imports(module_source):
    """Returns a list of unused import names in the module source."""
    tree = ast.parse(module_source)
    imported_names = set()
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Add only the top-level module name
                imported_names.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.name)
        elif isinstance(node, ast.Name):
            used_names.add(node.id)
    unused = imported_names - used_names
    return list(unused)


def count_functions(module_source):
    """Returns the number of function definitions in the module source."""
    tree = ast.parse(module_source)
    count = sum(1 for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef))
    return count


def count_classes(module_source):
    """Returns the number of class definitions in the module source."""
    tree = ast.parse(module_source)
    count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    return count


def find_unreachable_code(module_source):
    """
    Analyzes the module source code and returns warnings for unreachable code
    detected in function bodies (i.e., code that appears after a return or raise statement).
    """
    warnings = []
    tree = ast.parse(module_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Process statements sequentially in the function body
            found_termination = False
            for stmt in node.body:
                if found_termination:
                    warnings.append(
                        f"Unreachable code in function '{
                            node.name}' at line {stmt.lineno}."
                    )
                else:
                    # If a statement is a Return or Raise, mark subsequent statements as unreachable.
                    if isinstance(stmt, (ast.Return, ast.Raise)):
                        found_termination = True
    return warnings


def find_unused_variables(module_source):
    """
    Analyzes the module source code and returns a list of variable names that are assigned
    but never used. This is a basic analysis using AST and may not capture all edge cases.
    """
    class VariableAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.assigned = set()
            self.used = set()

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store):
                self.assigned.add(node.id)
            elif isinstance(node.ctx, ast.Load):
                self.used.add(node.id)
            self.generic_visit(node)

        # For function definitions, also treat arguments as assigned.
        def visit_FunctionDef(self, node):
            for arg in node.args.args:
                self.assigned.add(arg.arg)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            for arg in node.args.args:
                self.assigned.add(arg.arg)
            self.generic_visit(node)

    tree = ast.parse(module_source)
    analyzer = VariableAnalyzer()
    analyzer.visit(tree)
    # Variables that are assigned but never loaded (used) are considered unused.
    unused_vars = analyzer.assigned - analyzer.used
    return list(unused_vars)


def find_improvements(module_source):
    """
    Analyzes the module source code and returns a list of suggestions for improvements.
    Suggestions include:
      - Removing unused imports.
      - Removing unreachable code.
      - Adding missing docstrings to functions and classes.
      - Refactoring if there are too many functions.
    """
    suggestions = []

    # Suggest removal of unused imports
    unused = find_unused_imports(module_source)
    if unused:
        suggestions.append("Remove unused imports: " + ", ".join(unused))

    # Suggest removal of unreachable code
    unreachable = find_unreachable_code(module_source)
    if unreachable:
        suggestions.append(
            "Review and remove unreachable code found in functions.")

    # Check for missing docstrings in functions and classes
    tree = ast.parse(module_source)
    missing_docstring_funcs = []
    missing_docstring_classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if ast.get_docstring(node) is None:
                missing_docstring_funcs.append(node.name)
        elif isinstance(node, ast.ClassDef):
            if ast.get_docstring(node) is None:
                missing_docstring_classes.append(node.name)

    if missing_docstring_funcs:
        suggestions.append("Add docstrings to functions: " +
                           ", ".join(missing_docstring_funcs))
    if missing_docstring_classes:
        suggestions.append("Add docstrings to classes: " +
                           ", ".join(missing_docstring_classes))

    # Suggest refactoring if there are too many functions (arbitrary threshold)
    func_count = count_functions(module_source)
    if func_count > 10:
        suggestions.append(f"Consider refactoring; this module has {
                           func_count} functions.")

    return suggestions


def analyze_file(file_path):
    """Analyzes a single file and returns its module name and a report dictionary."""
    with open(file_path, 'r', encoding='utf-8') as f:
        module_source = f.read()

    module_name = os.path.splitext(os.path.basename(file_path))[0]

    module_report = {
        'unused_imports': find_unused_imports(module_source),
        'unused_variables': find_unused_variables(module_source),
        'function_count': count_functions(module_source),
        'class_count': count_classes(module_source),
        'unreachable_code': find_unreachable_code(module_source),
        'improvements': find_improvements(module_source)
    }

    return module_name, module_report


def generate_report(directory):
    """Walks through the directory (ignoring certain folders) and writes a JSON report."""
    report = {}
    for root, dirs, files in os.walk(directory):
        # Skip directories you want to ignore
        for d in ['venv', 'pyds', 'gen_ai', 'gen_ai_code']:
            if d in dirs:
                dirs.remove(d)
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                module_name, module_report = analyze_file(file_path)
                report[module_name] = module_report

    with open('code_quality_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)


if __name__ == "__main__":
    generate_report('./Bot')
