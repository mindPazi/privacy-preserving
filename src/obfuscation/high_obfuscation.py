"""
High-level obfuscation strategy.

This module implements a high obfuscation strategy that performs
aggressive transformations including replacing names with placeholders,
stripping comments, and removing docstrings.
"""

from typing import Dict, Set
import ast
import keyword
import re
from .base import BaseObfuscator


class HighObfuscator(BaseObfuscator):
    """
    High-level code obfuscator.

    Applies aggressive obfuscation techniques:
    - Replace all identifiers with generic placeholders
    - Strip all comments
    - Remove docstrings
    - Normalize whitespace

    Attributes:
        placeholder_prefix: Prefix for placeholder names.
        strip_comments: Whether to remove comments.
        strip_docstrings: Whether to remove docstrings.
        normalize_whitespace: Whether to normalize whitespace.
    """

    def __init__(
        self,
        placeholder_prefix: str = "PLACEHOLDER",
        strip_comments: bool = True,
        strip_docstrings: bool = True,
        normalize_whitespace: bool = True
    ) -> None:
        """
        Initialize the high-level obfuscator.

        Args:
            placeholder_prefix: Prefix for placeholder identifiers.
            strip_comments: Whether to remove comments.
            strip_docstrings: Whether to remove docstrings.
            normalize_whitespace: Whether to normalize whitespace.
        """
        super().__init__(
            name="HighObfuscator",
            description="Aggressive obfuscation with placeholders and comment removal"
        )
        self.placeholder_prefix = placeholder_prefix
        self.strip_comments = strip_comments
        self.strip_docstrings = strip_docstrings
        self.normalize_whitespace = normalize_whitespace
        self._mapping: Dict[str, str] = {}

    def obfuscate(self, code: str) -> str:
        """
        Apply high-level obfuscation to the code.

        Args:
            code: The original source code.

        Returns:
            Heavily obfuscated code.
        """
        if not code or not code.strip():
            return code

        self._mapping = {}
        result = code

        if self.strip_comments:
            result = self._strip_comments(result)

        result = self._replace_identifiers(result)

        if self.strip_docstrings:
            result = self._strip_docstrings(result)

        if self.normalize_whitespace:
            result = self._normalize_whitespace(result)

        return result

    def get_mapping(self) -> Dict[str, str]:
        """
        Get the identifier to placeholder mapping.

        Returns:
            Dictionary mapping original identifiers to placeholders.
        """
        return self._mapping.copy()

    def _strip_comments(self, code: str) -> str:
        """
        Remove all comments from the code.

        Args:
            code: Source code with comments.

        Returns:
            Code without comments.
        """
        lines = code.split('\n')
        result_lines = []
        
        for line in lines:
            in_string = False
            string_char = None
            new_line = []
            i = 0
            
            while i < len(line):
                char = line[i]
                
                if not in_string:
                    if char in ('"', "'"):
                        if i + 2 < len(line) and line[i:i+3] in ('"""', "'''"):
                            new_line.append(line[i:])
                            break
                        in_string = True
                        string_char = char
                        new_line.append(char)
                    elif char == '#':
                        break
                    else:
                        new_line.append(char)
                else:
                    new_line.append(char)
                    if char == string_char and (i == 0 or line[i-1] != '\\'):
                        in_string = False
                        string_char = None
                
                i += 1
            
            result_lines.append(''.join(new_line).rstrip())
        
        return '\n'.join(result_lines)

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

    def _replace_identifiers(self, code: str) -> str:
        """
        Replace all identifiers with placeholders.

        Args:
            code: Source code.

        Returns:
            Code with placeholder identifiers.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code
        
        reserved = self._get_reserved_keywords()
        identifiers = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id not in reserved:
                    identifiers.add(node.id)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                if node.name not in reserved:
                    identifiers.add(node.name)
                for arg in node.args.args:
                    if arg.arg not in reserved:
                        identifiers.add(arg.arg)
            elif isinstance(node, ast.arg):
                if node.arg not in reserved:
                    identifiers.add(node.arg)
        
        for i, identifier in enumerate(sorted(identifiers)):
            self._mapping[identifier] = self._generate_placeholder(i)
        
        result = code
        sorted_mapping = sorted(self._mapping.items(), key=lambda x: -len(x[0]))
        for original, placeholder in sorted_mapping:
            pattern = r'\b' + re.escape(original) + r'\b'
            result = re.sub(pattern, placeholder, result)
        
        return result

    def _normalize_whitespace(self, code: str) -> str:
        """
        Normalize whitespace in the code.

        Args:
            code: Source code.

        Returns:
            Code with normalized whitespace.
        """
        lines = code.split('\n')
        result_lines = []
        
        for line in lines:
            stripped = line.rstrip()
            if stripped:
                result_lines.append(stripped)
            elif result_lines and result_lines[-1]:
                result_lines.append('')
        
        while result_lines and not result_lines[-1]:
            result_lines.pop()
        while result_lines and not result_lines[0]:
            result_lines.pop(0)
        
        return '\n'.join(result_lines)

    def _get_reserved_keywords(self) -> Set[str]:
        """
        Get Python reserved keywords that should not be replaced.

        Returns:
            Set of reserved keyword strings.
        """
        return set(keyword.kwlist)

    def _generate_placeholder(self, index: int) -> str:
        """
        Generate a placeholder name based on index.

        Args:
            index: The placeholder index.

        Returns:
            Placeholder string (e.g., "PLACEHOLDER_0").
        """
        return f"{self.placeholder_prefix}_{index}"

    def get_privacy_level(self) -> str:
        """Return privacy level."""
        return "high"
