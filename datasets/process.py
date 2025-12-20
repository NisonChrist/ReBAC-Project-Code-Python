"""
Dataset Processing Module - Handles loading and processing datasets
"""

from pathlib import Path
import os
import re
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

    def load_datasets(self, datasets_dir_path: Path) -> dict[str, pd.DataFrame]:
        """
        Load all datasets from litroacp folder

        Returns:
            Dictionary with dataset names as keys and DataFrames as values
        """
        datasets = {}
        # litroacp_path = Path(__file__).parent / "litroacp"

        for file_name in sorted(os.listdir(datasets_dir_path)):
            file_path = datasets_dir_path / file_name
            try:
                if file_name.endswith(".jsonl"):
                    df = DatasetReader.read_jsonl(str(file_path))
                    datasets[file_name] = df
                    print(f"Loaded {file_name} with shape: {df.shape}")
                elif file_name.endswith(".xml"):
                    with open(file_path, "r", encoding="utf-8") as file:
                        policy_pattern = re.compile(
                            r"<Policy\s[^>]*>[\s\S]*?<\/Policy>"
                        )
                        xacml_content = file.read()
                        policies = policy_pattern.findall(xacml_content)
                        datasets[file_name] = pd.DataFrame({"policy": policies})
                        print(f"Loaded {file_name} with {len(policies)} policies.")
                else:
                    # print(f"Unsupported file format for {file_name}, skipping.")
                    continue
            except Exception as e:
                print(f"Error loading {file_name}: {e}")

        return datasets


__all__ = ["DatasetReader"]
