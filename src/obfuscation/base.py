"""
Base class for code obfuscation strategies.

This module defines the abstract interface that all
obfuscation strategies must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
import ast
import keyword


class BaseObfuscator(ABC):
    """
    Abstract base class for code obfuscation.

    All obfuscation strategies should inherit from this class
    and implement the required abstract methods.

    Attributes:
        name: Human-readable name of the obfuscation strategy.
        description: Brief description of the obfuscation technique.
    """

    def __init__(self, name: str, description: str) -> None:
        """
        Initialize the base obfuscator.

        Args:
            name: Human-readable name of the obfuscation strategy.
            description: Brief description of the obfuscation technique.
        """
        self.name = name
        self.description = description
        self._mapping: Dict[str, str] = {}

    @abstractmethod
    def obfuscate(self, code: str) -> str:
        """
        Apply obfuscation to the given code.

        Args:
            code: The original source code to obfuscate.

        Returns:
            The obfuscated code string.
        """
        pass

    @abstractmethod
    def get_mapping(self) -> Dict[str, str]:
        """
        Get the mapping of original to obfuscated identifiers.

        Returns:
            Dictionary mapping original names to obfuscated names.
        """
        pass

    def deobfuscate(self, code: str) -> str:
        """
        Reverse the obfuscation (if possible).

        Args:
            code: The obfuscated code.

        Returns:
            The deobfuscated code (best effort).
        """
        reverse_mapping = {v: k for k, v in self._mapping.items()}
        result = code
        for obfuscated, original in sorted(reverse_mapping.items(), key=lambda x: -len(x[0])):
            result = result.replace(obfuscated, original)
        return result

    def get_privacy_level(self) -> str:
        """
        Return the privacy level of this obfuscation strategy.

        Returns:
            String indicating privacy level (e.g., "low", "high").
        """
        return "base"

    def validate_code(self, code: str) -> bool:
        """
        Validate that the code is suitable for obfuscation.

        Args:
            code: The code to validate.

        Returns:
            True if the code can be obfuscated, False otherwise.
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def extract_identifiers(self, code: str) -> List[str]:
        """
        Extract all identifiers from the code.

        Args:
            code: The source code to analyze.

        Returns:
            List of identifier names found in the code.
        """
        identifiers = set()
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    identifiers.add(node.id)
                elif isinstance(node, ast.FunctionDef):
                    identifiers.add(node.name)
                    for arg in node.args.args:
                        identifiers.add(arg.arg)
                elif isinstance(node, ast.arg):
                    identifiers.add(node.arg)
        except SyntaxError:
            pass
        python_keywords = set(keyword.kwlist)
        python_builtins = set(dir(__builtins__)) if isinstance(__builtins__, dict) else set(dir(__builtins__))
        return [i for i in identifiers if i not in python_keywords and i not in python_builtins]

    def __repr__(self) -> str:
        """Return string representation of the obfuscator."""
        return f"{self.__class__.__name__}(name='{self.name}')"
