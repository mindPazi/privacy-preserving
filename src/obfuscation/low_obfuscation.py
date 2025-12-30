"""
Low-level obfuscation strategy.

This module implements a low obfuscation strategy that performs
minimal transformations such as renaming variables while preserving
overall code structure and readability.
"""

from typing import Dict, List, Optional
import ast
import keyword
import re
from .base import BaseObfuscator


class LowObfuscator(BaseObfuscator):
    """
    Low-level code obfuscator.

    Applies minimal obfuscation techniques:
    - Rename local variables to generic names (var1, var2, etc.)
    - Preserve function signatures and structure
    - Keep comments and docstrings intact

    Attributes:
        variable_prefix: Prefix for renamed variables.
        preserve_function_names: Whether to keep function names unchanged.
    """

    def __init__(
        self,
        variable_prefix: str = "var",
        preserve_function_names: bool = True
    ) -> None:
        """
        Initialize the low-level obfuscator.

        Args:
            variable_prefix: Prefix for renamed variables.
            preserve_function_names: Whether to keep function names unchanged.
        """
        super().__init__(
            name="LowObfuscator",
            description="Minimal obfuscation with variable renaming"
        )
        self.variable_prefix = variable_prefix
        self.preserve_function_names = preserve_function_names
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
        
        try:
            tree = self._parse_code(code)
        except SyntaxError:
            return code
        
        local_vars = self._find_local_variables(tree)
        
        for i, var in enumerate(sorted(local_vars)):
            self._mapping[var] = self._generate_new_name(i)
        
        return self._apply_renaming(code, self._mapping)

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
        
        for node in ast.walk(ast_node):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                function_names.add(node.name)
        
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, (ast.Store, ast.Load)):
                    if node.id not in python_keywords and node.id not in python_builtins:
                        if not (self.preserve_function_names and node.id in function_names):
                            variables.add(node.id)
            elif isinstance(node, ast.arg):
                if node.arg not in python_keywords and node.arg not in python_builtins:
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

    def get_privacy_level(self) -> str:
        """Return privacy level."""
        return "low"
