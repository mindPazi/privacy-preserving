"""
Tests for the data loading module.
"""

import unittest
from typing import List, Dict

import sys
sys.path.insert(0, '/home/claude')

from src.data import HumanEvalDataLoader


class TestHumanEvalDataLoader(unittest.TestCase):
    """
    Test cases for HumanEvalDataLoader class.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures.
        """
        self.loader = HumanEvalDataLoader(num_examples=5)

    def tearDown(self) -> None:
        """
        Clean up after tests.
        """
        self.loader = None

    def test_load_dataset(self) -> None:
        """
        Test that dataset loads correctly.
        """
        self.loader.load_dataset()
        self.assertIsNotNone(self.loader._dataset)
        self.assertEqual(len(self.loader), 5)

    def test_get_prompts(self) -> None:
        """
        Test prompt extraction.
        """
        prompts = self.loader.get_prompts()
        self.assertIsInstance(prompts, list)
        self.assertEqual(len(prompts), 5)
        for prompt in prompts:
            self.assertIsInstance(prompt, str)

    def test_get_canonical_solutions(self) -> None:
        """
        Test canonical solution extraction.
        """
        solutions = self.loader.get_canonical_solutions()
        self.assertIsInstance(solutions, list)
        self.assertEqual(len(solutions), 5)
        for solution in solutions:
            self.assertIsInstance(solution, str)

    def test_get_example(self) -> None:
        """
        Test single example retrieval.
        """
        example = self.loader.get_example(0)
        self.assertIsInstance(example, dict)
        self.assertIn('prompt', example)
        self.assertIn('canonical_solution', example)

    def test_invalid_index(self) -> None:
        """
        Test handling of invalid indices.
        """
        self.loader.load_dataset()
        with self.assertRaises(IndexError):
            self.loader.get_example(100)


if __name__ == "__main__":
    unittest.main()
