"""
Main entry point for privacy-preserving code completion experiments.

This script orchestrates the complete experimental pipeline:
1. Load HumanEval dataset
2. Apply obfuscation strategies
3. Generate code completions
4. Evaluate utility and privacy
5. Visualize results
"""

from typing import List, Dict, Any
from pathlib import Path
import argparse
import json
import numpy as np
# Internal imports (stubs)
from src.data import HumanEvalDataLoader
from src.obfuscation import LowObfuscator, HighObfuscator
from src.models import CodeCompletionModel
from src.evaluation import UtilityEvaluator, PrivacyEvaluator
from src.visualization import PrivacyUtilityPlotter


class ExperimentRunner:
    """
    Main experiment runner for privacy-utility trade-off analysis.

    Coordinates the complete experimental pipeline from data loading
    to visualization of results.

    Attributes:
        num_examples: Number of HumanEval examples to use.
        model_name: Name of the code completion model.
        output_dir: Directory for output files.
    """

    def __init__(
        self,
        num_examples: int = 20,
        model_name: str = "Salesforce/codet5-small",
        output_dir: str = "outputs"
    ) -> None:
        """
        Initialize the experiment runner.

        Args:
            num_examples: Number of HumanEval examples to use.
            model_name: Name of the code completion model.
            output_dir: Directory for output files.
        """
        self.num_examples = num_examples
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        
        self.data_loader = HumanEvalDataLoader(num_examples=num_examples)
        self.low_obfuscator = LowObfuscator()
        self.high_obfuscator = HighObfuscator()
        self.model = CodeCompletionModel(model_name=model_name)
        self.utility_evaluator = UtilityEvaluator()
        self.privacy_evaluator = PrivacyEvaluator()
        self.plotter = PrivacyUtilityPlotter()

    def setup(self) -> None:
        """
        Set up all experiment components.

        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_loader.load_dataset()
        self.model.load_model()

    def run_experiment(self) -> Dict[str, Any]:
        """
        Run the complete experiment.

        Returns:
            Dictionary containing all results.
        """
        self.setup()
        
        prompts = self.data_loader.get_prompts()
        canonical_solutions = self.data_loader.get_canonical_solutions()
        
        original_completions = self.generate_completions(prompts, "none")
        
        low_obfuscated_prompts = [self.low_obfuscator.obfuscate(p) for p in prompts]
        low_completions = self.generate_completions(low_obfuscated_prompts, "low")
        
        high_obfuscated_prompts = [self.high_obfuscator.obfuscate(p) for p in prompts]
        high_completions = self.generate_completions(high_obfuscated_prompts, "high")
        
        results = {
            'none': {
                'prompts': prompts,
                'obfuscated_prompts': prompts,
                'completions': original_completions,
                'canonical_solutions': canonical_solutions
            },
            'low': {
                'prompts': prompts,
                'obfuscated_prompts': low_obfuscated_prompts,
                'completions': low_completions,
                'canonical_solutions': canonical_solutions
            },
            'high': {
                'prompts': prompts,
                'obfuscated_prompts': high_obfuscated_prompts,
                'completions': high_completions,
                'canonical_solutions': canonical_solutions
            }
        }
        
        for level in ['none', 'low', 'high']:
            eval_results = self.evaluate_results(
                results[level]['completions'],
                results[level]['canonical_solutions'],
                results[level]['prompts'],
                results[level]['obfuscated_prompts']
            )
            results[level]['utility_scores'] = eval_results['utility_scores']
            results[level]['privacy_scores'] = eval_results['privacy_scores']
        
        return results

    def generate_completions(
        self,
        prompts: List[str],
        obfuscation_level: str = "none"
    ) -> List[str]:
        """
        Generate code completions for a set of prompts.

        Args:
            prompts: List of code prompts.
            obfuscation_level: Obfuscation level ("none", "low", "high").

        Returns:
            List of generated completions.
        """
        return self.model.generate_completions_batch(prompts)

    def evaluate_results(
        self,
        completions: List[str],
        canonical_solutions: List[str],
        original_prompts: List[str],
        obfuscated_prompts: List[str]
    ) -> Dict[str, List[float]]:
        """
        Evaluate generated completions.

        Args:
            completions: Generated code completions.
            canonical_solutions: Reference solutions.
            original_prompts: Original prompts.
            obfuscated_prompts: Obfuscated prompts.

        Returns:
            Dictionary with utility and privacy scores.
        """
        
        utility_scores = [
            self.utility_evaluator.get_utility_score(comp, ref)
            for comp, ref in zip(completions, canonical_solutions)
        ]
        
        privacy_scores = self.privacy_evaluator.compute_privacy_batch(
            original_prompts, obfuscated_prompts
        )
        
        return {
            'utility_scores': utility_scores,
            'privacy_scores': privacy_scores
        }

    def visualize_results(self, results: Dict[str, Any]) -> None:
        """
        Create visualizations of experimental results.

        Args:
            results: Dictionary containing experiment results.
        """
        all_privacy = []
        all_utility = []
        all_labels = []
        
        for level in ['none', 'low', 'high']:
            all_privacy.extend(results[level]['privacy_scores'])
            all_utility.extend(results[level]['utility_scores'])
            all_labels.extend([level] * len(results[level]['privacy_scores']))
        
        fig = self.plotter.create_scatter_plot(
            all_privacy,
            all_utility,
            labels=all_labels,
            title="Privacy-Utility Trade-off by Obfuscation Level"
        )
        
        self.plotter.save_figure(fig, self.output_dir / "privacy_utility_scatter.png")


    def save_results(
        self,
        results: Dict[str, Any],
        filepath: Path
    ) -> None:
        """
        Save experimental results to file.

        Args:
            results: Dictionary containing experiment results.
            filepath: Output file path.
        """
        
        save_data = {}
        for level in ['none', 'low', 'high']:
            save_data[level] = {
                'utility_scores': results[level]['utility_scores'],
                'privacy_scores': results[level]['privacy_scores']
            }
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)

    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a text report of the experimental results.

        Args:
            results: Dictionary containing experiment results.

        Returns:
            Formatted report string.
        """
        report = []
        report.append("=" * 60)
        report.append("Privacy-Utility Trade-off Experiment Report")
        report.append("=" * 60)
        report.append("")
        
        for level in ['none', 'low', 'high']:
            utility = results[level]['utility_scores']
            privacy = results[level]['privacy_scores']
            
            report.append(f"Obfuscation Level: {level.upper()}")
            report.append("-" * 40)
            report.append(f"  Utility Score (ROUGE-L):")
            report.append(f"    Mean: {np.mean(utility):.4f}")
            report.append(f"    Std:  {np.std(utility):.4f}")
            report.append(f"  Privacy Score (Normalized Levenshtein):")
            report.append(f"    Mean: {np.mean(privacy):.4f}")
            report.append(f"    Std:  {np.std(privacy):.4f}")
            report.append("")
        
        return "\n".join(report)


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
    description="Privacy-Preserving Code Completion Experiment"
    )
    parser.add_argument(
        "--num_examples", type=int, default=20,
        help="Number of HumanEval examples to use"
    )
    parser.add_argument(
        "--model_name", type=str, default="Salesforce/codet5-small",
        help="HuggingFace model identifier"
    )
    parser.add_argument(
        "--output_dir", type=str, default="outputs",
        help="Directory for output files"
    )
    parser.add_argument(
        "--device", type=str, default="cpu",
        help="Device for model inference (cpu/cuda)"
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Main entry point.
    """
    args = parse_arguments()
    
    runner = ExperimentRunner(
        num_examples=args.num_examples,
        model_name=args.model_name,
        output_dir=args.output_dir
    )
    
    if args.device:
        runner.model.device = args.device
    
    results = runner.run_experiment()
    
    runner.visualize_results(results)
    runner.save_results(results, Path(args.output_dir) / "results.json")
    
    report = runner.generate_report(results)
    print(report)


if __name__ == "__main__":
    main()
