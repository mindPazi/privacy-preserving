"""
Low-level obfuscation strategy.

This module implements a low obfuscation strategy that performs
minimal transformations such as renaming variables while preserving
overall code structure and readability.
"""

from typing import Dict, List
import ast
import keyword
import re
from .base import BaseObfuscator


class LowObfuscator(BaseObfuscator):
    """
    Low-level code obfuscator.

    Applies minimal obfuscation techniques:
    - Rename local variables and parameters to generic names (var1, var2, etc.)
    - Preserve function names and type annotations
    - Remove docstrings to avoid inconsistencies

    Attributes:
        variable_prefix: Prefix for renamed variables.
        preserve_function_names: Whether to keep function names unchanged.
        strip_docstrings: Whether to remove docstrings.
    """

    def __init__(
        self,
        variable_prefix: str = "var",
        preserve_function_names: bool = True,
        strip_docstrings: bool = True
    ) -> None:
        """
        Initialize the low-level obfuscator.

        Args:
            variable_prefix: Prefix for renamed variables.
            preserve_function_names: Whether to keep function names unchanged.
            strip_docstrings: Whether to remove docstrings.
        """
        super().__init__(
            name="LowObfuscator",
            description="Minimal obfuscation with variable renaming"
        )
        self.variable_prefix = variable_prefix
        self.preserve_function_names = preserve_function_names
        self.strip_docstrings = strip_docstrings
        self._mapping: Dict[str, str] = {}

    def obfuscate(self, code: str) -> str:
        """
        Apply low-level obfuscation to the code.

        Args:
            code: The original source code.

        Returns:
            Code with renamed variables.
        """
        if not code or not code.strip():
            return code

        self._mapping = {}
        result = code

        try:
            tree = self._parse_code(result)
        except SyntaxError:
            return code

        local_vars = self._find_local_variables(tree)

        for i, var in enumerate(sorted(local_vars)):
            self._mapping[var] = self._generate_new_name(i)

        result = self._apply_renaming(result, self._mapping)

        if self.strip_docstrings:
            result = self._strip_docstrings(result)

        return result

    def get_mapping(self) -> Dict[str, str]:
        """
        Get the variable name mapping.

        Returns:
            Dictionary mapping original variable names to new names.
        """
        return self._mapping.copy()

    def _parse_code(self, code: str):
        """
        Parse the code into an AST.

        Args:
            code: Source code string.

        Returns:
            Parsed AST node.
        """
        return ast.parse(code)

    def _find_local_variables(self, ast_node) -> List[str]:
        """
        Find all local variable names in the AST.

        Args:
            ast_node: The parsed AST.

        Returns:
            List of local variable names.
        """
        variables = set()
        function_names = set()
        python_keywords = set(keyword.kwlist)
        python_builtins = {'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict',
                          'set', 'tuple', 'bool', 'type', 'isinstance', 'hasattr', 'getattr',
                          'setattr', 'open', 'input', 'abs', 'all', 'any', 'bin', 'chr',
                          'enumerate', 'filter', 'format', 'hex', 'id', 'iter', 'map', 'max',
                          'min', 'next', 'oct', 'ord', 'pow', 'repr', 'reversed', 'round',
                          'slice', 'sorted', 'sum', 'super', 'zip', 'True', 'False', 'None'}
        typing_types = {'List', 'Dict', 'Set', 'Tuple', 'Optional', 'Union', 'Any',
                       'Callable', 'Iterable', 'Iterator', 'Sequence', 'Mapping',
                       'TypeVar', 'Generic', 'Protocol', 'Literal', 'Final',
                       'ClassVar', 'Type', 'cast', 'overload', 'TypedDict'}

        for node in ast.walk(ast_node):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                function_names.add(node.name)

        reserved = python_keywords | python_builtins | typing_types

        for node in ast.walk(ast_node):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, (ast.Store, ast.Load)):
                    if node.id not in reserved:
                        if not (self.preserve_function_names and node.id in function_names):
                            variables.add(node.id)
            elif isinstance(node, ast.arg):
                if node.arg not in reserved:
                    variables.add(node.arg)

        if self.preserve_function_names:
            variables -= function_names

        return list(variables)

    def _generate_new_name(self, index: int) -> str:
        """
        Generate a new variable name based on index.

        Args:
            index: The variable index.

        Returns:
            New variable name (e.g., "var1").
        """
        return f"{self.variable_prefix}{index + 1}"

    def _apply_renaming(self, code: str, mapping: Dict[str, str]) -> str:
        """
        Apply the variable renaming to the code.

        Args:
            code: Original source code.
            mapping: Variable name mapping.

        Returns:
            Code with renamed variables.
        """
        result = code
        sorted_mapping = sorted(mapping.items(), key=lambda x: -len(x[0]))
        
        for original, new in sorted_mapping:
            pattern = r'\b' + re.escape(original) + r'\b'
            result = re.sub(pattern, new, result)
        
        return result

    def _strip_docstrings(self, code: str) -> str:
        """
        Remove all docstrings from the code.

        Args:
            code: Source code with docstrings.

        Returns:
            Code without docstrings.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code

        docstring_positions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                    docstring_node = node.body[0]
                    if hasattr(docstring_node, 'lineno') and hasattr(docstring_node, 'end_lineno'):
                        docstring_positions.append((docstring_node.lineno, docstring_node.end_lineno))

        if not docstring_positions:
            return code

        lines = code.split('\n')
        lines_to_remove = set()
        for start, end in docstring_positions:
            for i in range(start - 1, end):
                if i < len(lines):
                    lines_to_remove.add(i)

        result_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
        return '\n'.join(result_lines)

    def get_privacy_level(self) -> str:
        """Return privacy level."""
        return "low"
