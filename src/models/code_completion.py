"""
Code completion model wrapper.

This module provides a unified interface for code completion models,
specifically designed to work with models like Salesforce/codet5-small.
"""

from typing import List, Dict, Any, Optional
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch


class CodeCompletionModel:
    """
    Wrapper for code completion models.

    Provides a unified interface for generating code completions
    using transformer-based models from HuggingFace.

    Attributes:
        model_name: The HuggingFace model identifier.
        device: The device to run inference on (cpu/cuda).
        max_length: Maximum length of generated completions.
    """

    def __init__(
        self,
        model_name: str = "Salesforce/codet5-small",
        device: str = "cpu",
        max_length: int = 256
    ) -> None:
        """
        Initialize the code completion model.

        Args:
            model_name: The HuggingFace model identifier.
            device: The device to run inference on.
            max_length: Maximum length of generated completions.
        """
        self.model_name = model_name
        self.device = device
        self.max_length = max_length
        self.model = None
        self.tokenizer = None
        self._generation_params = {
            'max_length': max_length,
            'num_beams': 1,
            'temperature': 1.0,
            'top_p': 1.0,
            'do_sample': False
        }

    def load_model(self) -> None:
        """
        Load the model and tokenizer from HuggingFace.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()

    def generate_completion(self, prompt: str) -> str:
        """
        Generate a code completion for the given prompt.

        Args:
            prompt: The code prompt to complete.

        Returns:
            The generated code completion.
        """
        if self.model is None:
            self.load_model()
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=self._generation_params['max_length'],
                num_beams=self._generation_params['num_beams'],
                do_sample=self._generation_params['do_sample'],
                temperature=self._generation_params['temperature'] if self._generation_params['do_sample'] else 1.0,
                top_p=self._generation_params['top_p'] if self._generation_params['do_sample'] else 1.0
            )
        
        completion = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return completion

    def generate_completions_batch(
        self,
        prompts: List[str],
        batch_size: int = 8
    ) -> List[str]:
        """
        Generate completions for multiple prompts.

        Args:
            prompts: List of code prompts.
            batch_size: Number of prompts to process at once.

        Returns:
            List of generated completions.
        """
        if self.model is None:
            self.load_model()
        
        completions = []
        
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            inputs = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=self._generation_params['max_length'],
                    num_beams=self._generation_params['num_beams'],
                    do_sample=self._generation_params['do_sample']
                )
            
            batch_completions = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
            completions.extend(batch_completions)
        
        return completions

    def set_generation_params(
        self,
        max_length: Optional[int] = None,
        num_beams: int = 1,
        temperature: float = 1.0,
        top_p: float = 1.0,
        do_sample: bool = False
    ) -> None:
        """
        Configure generation parameters.

        Args:
            max_length: Maximum generation length.
            num_beams: Number of beams for beam search.
            temperature: Sampling temperature.
            top_p: Nucleus sampling probability.
            do_sample: Whether to use sampling.
        """
        if max_length is not None:
            self._generation_params['max_length'] = max_length
        self._generation_params['num_beams'] = num_beams
        self._generation_params['temperature'] = temperature
        self._generation_params['top_p'] = top_p
        self._generation_params['do_sample'] = do_sample

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            Dictionary containing model metadata.
        """
        return {
            'model_name': self.model_name,
            'device': self.device,
            'max_length': self.max_length,
            'is_loaded': self.model is not None,
            'generation_params': self._generation_params.copy()
        }

    def to_device(self, device: str) -> None:
        """
        Move the model to a different device.

        Args:
            device: Target device (cpu/cuda).
        """
        self.device = device
        if self.model is not None:
            self.model.to(device)

    def __repr__(self) -> str:
        """Return string representation of the model."""
        return f"CodeCompletionModel(model_name='{self.model_name}', device='{self.device}')"
