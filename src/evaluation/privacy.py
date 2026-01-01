"""
Privacy scoring module.

This module provides metrics for evaluating the privacy preservation
of obfuscated prompts by measuring their distance from original prompts.
"""

from typing import List, Dict, Any, Optional, Tuple
import Levenshtein
import numpy as np


class PrivacyEvaluator:
    """
    Evaluator for prompt privacy.

    Measures how different the obfuscated prompts are from the
    original prompts using distance metrics like Levenshtein distance.

    Attributes:
        normalization: Type of normalization to apply to distances.
    """

    def __init__(
        self,
        normalization: str = "max_length"
    ) -> None:
        """
        Initialize the privacy evaluator.

        Args:
            normalization: How to normalize distances ("max_length", "mean_length", "none").
        """
        self.normalization = normalization

    def compute_levenshtein_distance(
        self,
        original: str,
        obfuscated: str
    ) -> int:
        """
        Compute the Levenshtein (edit) distance between two strings.

        Args:
            original: The original prompt.
            obfuscated: The obfuscated prompt.

        Returns:
            The Levenshtein distance (number of edits).
        """
        return Levenshtein.distance(original, obfuscated)

    def compute_normalized_distance(
        self,
        original: str,
        obfuscated: str
    ) -> float:
        """
        Compute normalized Levenshtein distance.

        Args:
            original: The original prompt.
            obfuscated: The obfuscated prompt.

        Returns:
            Normalized distance between 0 and 1.
        """
        if not original and not obfuscated:
            return 0.0
        
        distance = self.compute_levenshtein_distance(original, obfuscated)
        
        if self.normalization == "max_length":
            max_len = max(len(original), len(obfuscated))
            if max_len == 0:
                return 0.0
            return distance / max_len
        elif self.normalization == "mean_length":
            mean_len = (len(original) + len(obfuscated)) / 2
            if mean_len == 0:
                return 0.0
            return distance / mean_len
        else:
            return float(distance)

    def get_privacy_score(
        self,
        original: str,
        obfuscated: str
    ) -> float:
        """
        Get a privacy score for an obfuscated prompt.

        Higher scores indicate better privacy (more different from original).

        Args:
            original: The original prompt.
            obfuscated: The obfuscated prompt.

        Returns:
            Privacy score between 0 and 1.
        """
        return self.compute_normalized_distance(original, obfuscated)

    def compute_privacy_batch(
        self,
        original_list: List[str],
        obfuscated_list: List[str]
    ) -> List[float]:
        """
        Compute privacy scores for multiple pairs.

        Args:
            original_list: List of original prompts.
            obfuscated_list: List of obfuscated prompts.

        Returns:
            List of privacy scores.
        """
        return [
            self.get_privacy_score(orig, obf)
            for orig, obf in zip(original_list, obfuscated_list)
        ]

    def compute_jaccard_distance(
        self,
        original: str,
        obfuscated: str
    ) -> float:
        """
        Compute Jaccard distance between token sets.

        Args:
            original: The original prompt.
            obfuscated: The obfuscated prompt.

        Returns:
            Jaccard distance between 0 and 1.
        """
        original_tokens = set(original.split())
        obfuscated_tokens = set(obfuscated.split())
        
        if not original_tokens and not obfuscated_tokens:
            return 0.0
        
        intersection = len(original_tokens & obfuscated_tokens)
        union = len(original_tokens | obfuscated_tokens)
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        return 1.0 - jaccard_similarity

    def compute_cosine_distance(
        self,
        original: str,
        obfuscated: str
    ) -> float:
        """
        Compute cosine distance between TF-IDF vectors.

        Args:
            original: The original prompt.
            obfuscated: The obfuscated prompt.

        Returns:
            Cosine distance between 0 and 1.
        """
        original_tokens = original.split()
        obfuscated_tokens = obfuscated.split()
        
        all_tokens = list(set(original_tokens + obfuscated_tokens))
        
        if not all_tokens:
            return 0.0
        
        vec1 = np.array([original_tokens.count(t) for t in all_tokens], dtype=float)
        vec2 = np.array([obfuscated_tokens.count(t) for t in all_tokens], dtype=float)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 1.0
        
        cosine_similarity = dot_product / (norm1 * norm2)
        return 1.0 - cosine_similarity

    def aggregate_scores(
        self,
        scores: List[float]
    ) -> Dict[str, float]:
        """
        Aggregate privacy scores across multiple examples.

        Args:
            scores: List of privacy scores.

        Returns:
            Aggregated statistics (mean, std, min, max).
        """
        if not scores:
            return {}
        
        return {
            'mean': float(np.mean(scores)),
            'std': float(np.std(scores)),
            'min': float(np.min(scores)),
            'max': float(np.max(scores))
        }

    def __repr__(self) -> str:
        """Return string representation of the evaluator."""
        return f"PrivacyEvaluator(normalization='{self.normalization}')"
