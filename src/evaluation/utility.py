"""
Utility scoring module.

This module provides metrics for evaluating the utility of
code completions by comparing them to canonical solutions.
"""

from typing import List, Dict, Any, Optional, Tuple
from rouge_score import rouge_scorer
import numpy as np


class UtilityEvaluator:
    """
    Evaluator for code completion utility.

    Measures how well the generated completions match the
    canonical solutions using various metrics like ROUGE.

    Attributes:
        rouge_types: List of ROUGE metric types to compute.
    """

    def __init__(
        self,
        rouge_types: Optional[List[str]] = None
    ) -> None:
        """
        Initialize the utility evaluator.

        Args:
            rouge_types: ROUGE metric types (default: ["rouge1", "rouge2", "rougeL"]).
        """
        if rouge_types is None:
            rouge_types = ["rouge1", "rouge2", "rougeL"]
        self.rouge_types = rouge_types
        self._scorer = rouge_scorer.RougeScorer(rouge_types, use_stemmer=True)

    def compute_rouge_score(
        self,
        generated: str,
        reference: str
    ) -> Dict[str, float]:
        """
        Compute ROUGE scores between generated and reference text.

        Args:
            generated: The generated completion.
            reference: The canonical solution.

        Returns:
            Dictionary of ROUGE scores.
        """
        if not generated or not reference:
            return {rt: 0.0 for rt in self.rouge_types}
        
        scores = self._scorer.score(reference, generated)
        return {rt: scores[rt].fmeasure for rt in self.rouge_types}

    def compute_rouge_batch(
        self,
        generated_list: List[str],
        reference_list: List[str]
    ) -> List[Dict[str, float]]:
        """
        Compute ROUGE scores for multiple pairs.

        Args:
            generated_list: List of generated completions.
            reference_list: List of canonical solutions.

        Returns:
            List of ROUGE score dictionaries.
        """
        results = []
        for gen, ref in zip(generated_list, reference_list):
            results.append(self.compute_rouge_score(gen, ref))
        return results

    def get_utility_score(
        self,
        generated: str,
        reference: str,
        metric: str = "rougeL"
    ) -> float:
        """
        Get a single utility score for a completion.

        Args:
            generated: The generated completion.
            reference: The canonical solution.
            metric: Which ROUGE metric to use.

        Returns:
            Utility score between 0 and 1.
        """
        scores = self.compute_rouge_score(generated, reference)
        return scores.get(metric, 0.0)

    def compute_exact_match(
        self,
        generated: str,
        reference: str
    ) -> bool:
        """
        Check if generated code exactly matches reference.

        Args:
            generated: The generated completion.
            reference: The canonical solution.

        Returns:
            True if exact match, False otherwise.
        """
        gen_normalized = ' '.join(generated.split())
        ref_normalized = ' '.join(reference.split())
        return gen_normalized == ref_normalized

    def compute_bleu_score(
        self,
        generated: str,
        reference: str
    ) -> float:
        """
        Compute BLEU score between generated and reference.

        Args:
            generated: The generated completion.
            reference: The canonical solution.

        Returns:
            BLEU score between 0 and 1.
        """
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        
        if not generated or not reference:
            return 0.0
        
        reference_tokens = reference.split()
        generated_tokens = generated.split()
        
        if not reference_tokens or not generated_tokens:
            return 0.0
        
        smoothing = SmoothingFunction().method1
        try:
            score = sentence_bleu([reference_tokens], generated_tokens, smoothing_function=smoothing)
        except:
            score = 0.0
        
        return score

    def aggregate_scores(
        self,
        scores: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Aggregate scores across multiple examples.

        Args:
            scores: List of score dictionaries.

        Returns:
            Aggregated statistics (mean, std, min, max).
        """
        if not scores:
            return {}
        
        aggregated = {}
        all_keys = set()
        for s in scores:
            all_keys.update(s.keys())
        
        for key in all_keys:
            values = [s.get(key, 0.0) for s in scores]
            aggregated[f"{key}_mean"] = float(np.mean(values))
            aggregated[f"{key}_std"] = float(np.std(values))
            aggregated[f"{key}_min"] = float(np.min(values))
            aggregated[f"{key}_max"] = float(np.max(values))
        
        return aggregated

    def __repr__(self) -> str:
        """Return string representation of the evaluator."""
        return f"UtilityEvaluator(rouge_types={self.rouge_types})"
