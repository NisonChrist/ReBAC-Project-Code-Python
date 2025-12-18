"""
ReBAC Project - Relation-Based Access Control Policy Generation
Main package initialization
"""

from policy_gen import LLM, Prompt
from datasets import DatasetReader

__version__ = "1.0.0"
__all__ = [
    "LLM",
    "Prompt",
    "DatasetReader",
]
