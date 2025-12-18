"""
Dataset Processing Module - Handles loading and processing datasets
"""

from pathlib import Path
import os
import pandas as pd


class DatasetReader:
    """Reader class for loading different dataset formats"""

    @staticmethod
    def read_jsonl(abs_path: str) -> pd.DataFrame:
        """Read JSONL format file"""
        return pd.read_json(abs_path, lines=True)

    @staticmethod
    def read_csv(abs_path: str) -> pd.DataFrame:
        """Read CSV format file"""
        return pd.read_csv(abs_path)


def load_litroacp_datasets() -> dict[str, pd.DataFrame]:
    """
    Load all datasets from litroacp folder

    Returns:
        Dictionary with dataset names as keys and DataFrames as values
    """
    datasets = {}
    litroacp_path = Path(__file__).parent / "litroacp"

    for file_name in sorted(os.listdir(litroacp_path)):
        file_path = litroacp_path / file_name

        try:
            if file_name.endswith(".jsonl"):
                df = DatasetReader.read_jsonl(str(file_path))
                datasets[file_name] = df
                print(f"Loaded {file_name} with shape: {df.shape}")
            elif file_name.endswith(".csv"):
                df = DatasetReader.read_csv(str(file_path))
                datasets[file_name] = df
                print(f"Loaded {file_name} with shape: {df.shape}")
        except Exception as e:
            print(f"Error loading {file_name}: {e}")

    return datasets


__all__ = ["DatasetReader", "load_litroacp_datasets"]
