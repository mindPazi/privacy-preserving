"""
Code obfuscation module.

This module provides various levels of code obfuscation
for privacy-preserving code completion experiments.
"""

from .base import BaseObfuscator
from .low_obfuscation import LowObfuscator
from .high_obfuscation import HighObfuscator

__all__ = [
    "BaseObfuscator",
    "LowObfuscator",
    "HighObfuscator",
]
