"""
Data loader for the OpenAI HumanEval dataset.

This module provides functionality to load and preprocess
examples from the openai/openai_humaneval test split.
"""

from typing import List, Dict, Any, Optional
from datasets import load_dataset


class HumanEvalDataLoader:
    """
    Loader for the OpenAI HumanEval dataset.

    Attributes:
        dataset_name: The HuggingFace dataset identifier.
        split: The dataset split to use (default: "test").
        num_examples: Number of examples to load.
    """

    def __init__(
        self,
        dataset_name: str = "openai/openai_humaneval",
        split: str = "test",
        num_examples: int = 20
    ) -> None:
        """
        Initialize the HumanEval data loader.

        Args:
            dataset_name: The HuggingFace dataset identifier.
            split: The dataset split to use.
            num_examples: Number of examples to load from the dataset.
        """
        self.dataset_name = dataset_name
        self.split = split
        self.num_examples = num_examples
        self._dataset = None

    def load_dataset(self) -> None:
        """
        Load the dataset from HuggingFace.
        """
        dataset = load_dataset(self.dataset_name, split=self.split)
        self._dataset = dataset.select(range(min(self.num_examples, len(dataset))))

    def get_prompts(self) -> List[str]:
        """
        Extract code prompts from the dataset.

        Returns:
            List of code prompt strings.
        """
        if self._dataset is None:
            self.load_dataset()
        return [example['prompt'] for example in self._dataset]

    def get_canonical_solutions(self) -> List[str]:
        """
        Extract canonical solutions from the dataset.

        Returns:
            List of canonical solution strings.
        """
        if self._dataset is None:
            self.load_dataset()
        return [example['canonical_solution'] for example in self._dataset]

    def get_example(self, index: int) -> Dict[str, Any]:
        """
        Get a single example by index.

        Args:
            index: The index of the example to retrieve.

        Returns:
            Dictionary containing prompt, canonical_solution, and metadata.
        """
        if self._dataset is None:
            self.load_dataset()
        if index < 0 or index >= len(self._dataset):
            raise IndexError(f"Index {index} out of range for dataset with {len(self._dataset)} examples")
        example = self._dataset[index]
        return {
            'prompt': example['prompt'],
            'canonical_solution': example['canonical_solution'],
            'task_id': example.get('task_id', ''),
            'entry_point': example.get('entry_point', ''),
            'test': example.get('test', '')
        }

    def __len__(self) -> int:
        """
        Return the number of loaded examples.
        """
        if self._dataset is None:
            self.load_dataset()
        return len(self._dataset)

    def __iter__(self):
        """
        Iterate over all loaded examples.
        """
        if self._dataset is None:
            self.load_dataset()
        for i in range(len(self._dataset)):
            yield self.get_example(i)
