"""
Tests for the evaluation module.
"""

import unittest
from typing import Dict, List

import sys
sys.path.insert(0, '/home/claude')

from src.evaluation import UtilityEvaluator, PrivacyEvaluator


class TestUtilityEvaluator(unittest.TestCase):
    """
    Test cases for UtilityEvaluator class.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures.
        """
        self.evaluator = UtilityEvaluator()

    def test_compute_rouge_score(self) -> None:
        """
        Test ROUGE score computation.
        """
        generated = "The quick brown fox"
        reference = "The quick brown fox jumps"
        scores = self.evaluator.compute_rouge_score(generated, reference)
        self.assertIn('rouge1', scores)
        self.assertIn('rouge2', scores)
        self.assertIn('rougeL', scores)
        for score in scores.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_compute_rouge_identical(self) -> None:
        """
        Test ROUGE score for identical strings.
        """
        text = "The quick brown fox"
        scores = self.evaluator.compute_rouge_score(text, text)
        self.assertAlmostEqual(scores['rougeL'], 1.0, places=5)

    def test_compute_rouge_empty(self) -> None:
        """
        Test ROUGE score for empty strings.
        """
        scores = self.evaluator.compute_rouge_score("", "")
        for score in scores.values():
            self.assertEqual(score, 0.0)

    def test_compute_rouge_batch(self) -> None:
        """
        Test batch ROUGE computation.
        """
        generated = ["hello world", "foo bar"]
        reference = ["hello world", "baz qux"]
        results = self.evaluator.compute_rouge_batch(generated, reference)
        self.assertEqual(len(results), 2)

    def test_compute_bleu_score(self) -> None:
        """
        Test BLEU score computation.
        """
        generated = "The quick brown fox"
        reference = "The quick brown fox jumps"
        score = self.evaluator.compute_bleu_score(generated, reference)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_aggregate_scores(self) -> None:
        """
        Test score aggregation.
        """
        scores = [{'rouge1': 0.5, 'rougeL': 0.6}, {'rouge1': 0.7, 'rougeL': 0.8}]
        aggregated = self.evaluator.aggregate_scores(scores)
        self.assertIn('rouge1_mean', aggregated)
        self.assertIn('rouge1_std', aggregated)
        self.assertIn('rouge1_min', aggregated)
        self.assertIn('rouge1_max', aggregated)


class TestPrivacyEvaluator(unittest.TestCase):
    """
    Test cases for PrivacyEvaluator class.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures.
        """
        self.evaluator = PrivacyEvaluator()

    def test_compute_levenshtein_distance(self) -> None:
        """
        Test Levenshtein distance computation.
        """
        distance = self.evaluator.compute_levenshtein_distance("kitten", "sitting")
        self.assertEqual(distance, 3)

    def test_compute_levenshtein_identical(self) -> None:
        """
        Test Levenshtein distance for identical strings.
        """
        distance = self.evaluator.compute_levenshtein_distance("hello", "hello")
        self.assertEqual(distance, 0)

    def test_compute_normalized_distance(self) -> None:
        """
        Test normalized distance computation.
        """
        distance = self.evaluator.compute_normalized_distance("abc", "def")
        self.assertGreaterEqual(distance, 0.0)
        self.assertLessEqual(distance, 1.0)

    def test_get_privacy_score(self) -> None:
        """
        Test privacy score computation.
        """
        original = "x = 5"
        obfuscated = "PLACEHOLDER_0 = 5"
        score = self.evaluator.get_privacy_score(original, obfuscated)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_compute_privacy_batch(self) -> None:
        """
        Test batch privacy computation.
        """
        originals = ["hello", "world"]
        obfuscated = ["hallo", "werld"]
        scores = self.evaluator.compute_privacy_batch(originals, obfuscated)
        self.assertEqual(len(scores), 2)

    def test_compute_jaccard_distance(self) -> None:
        """
        Test Jaccard distance computation.
        """
        distance = self.evaluator.compute_jaccard_distance("hello world", "hello there")
        self.assertGreaterEqual(distance, 0.0)
        self.assertLessEqual(distance, 1.0)


if __name__ == "__main__":
    unittest.main()
