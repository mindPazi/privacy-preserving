"""
Tests for the obfuscation module.
"""

import unittest
from typing import Dict

import sys
sys.path.insert(0, '/home/claude')

from src.obfuscation import LowObfuscator, HighObfuscator


class TestLowObfuscator(unittest.TestCase):
    """
    Test cases for LowObfuscator class.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures.
        """
        self.obfuscator = LowObfuscator()

    def test_obfuscate_renames_variables(self) -> None:
        """
        Test that variables are renamed correctly.
        """
        code = "x = 5\ny = x + 1"
        result = self.obfuscator.obfuscate(code)
        self.assertNotIn("x", result.split())
        self.assertNotIn("y", result.split())

    def test_obfuscate_preserves_function_names(self) -> None:
        """
        Test that function names are preserved.
        """
        code = "def my_function(arg):\n    return arg + 1"
        result = self.obfuscator.obfuscate(code)
        self.assertIn("my_function", result)

    def test_obfuscate_preserves_comments(self) -> None:
        """
        Test that comments are preserved.
        """
        code = "# This is a comment\nx = 5"
        result = self.obfuscator.obfuscate(code)
        self.assertIn("# This is a comment", result)

    def test_get_mapping(self) -> None:
        """
        Test that mapping is generated correctly.
        """
        code = "x = 5\ny = 10"
        self.obfuscator.obfuscate(code)
        mapping = self.obfuscator.get_mapping()
        self.assertIsInstance(mapping, dict)
        self.assertGreater(len(mapping), 0)

    def test_obfuscate_empty_code(self) -> None:
        """
        Test handling of empty code input.
        """
        result = self.obfuscator.obfuscate("")
        self.assertEqual(result, "")


class TestHighObfuscator(unittest.TestCase):
    """
    Test cases for HighObfuscator class.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures.
        """
        self.obfuscator = HighObfuscator()

    def test_obfuscate_strips_comments(self) -> None:
        """
        Test that comments are removed.
        """
        code = "x = 5  # This is a comment"
        result = self.obfuscator.obfuscate(code)
        self.assertNotIn("# This is a comment", result)

    def test_obfuscate_strips_docstrings(self) -> None:
        """
        Test that docstrings are removed.
        """
        code = 'def foo():\n    """This is a docstring."""\n    return 1'
        result = self.obfuscator.obfuscate(code)
        self.assertNotIn("docstring", result)

    def test_obfuscate_replaces_identifiers(self) -> None:
        """
        Test that identifiers are replaced with placeholders.
        """
        code = "my_var = 5"
        result = self.obfuscator.obfuscate(code)
        self.assertIn("PLACEHOLDER", result)

    def test_obfuscate_preserves_keywords(self) -> None:
        """
        Test that Python keywords are not replaced.
        """
        code = "def foo():\n    return True"
        result = self.obfuscator.obfuscate(code)
        self.assertIn("def", result)
        self.assertIn("return", result)

    def test_get_mapping(self) -> None:
        """
        Test that mapping is generated correctly.
        """
        code = "x = 5\ny = 10"
        self.obfuscator.obfuscate(code)
        mapping = self.obfuscator.get_mapping()
        self.assertIsInstance(mapping, dict)


if __name__ == "__main__":
    unittest.main()
