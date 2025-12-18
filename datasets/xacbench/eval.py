"""
XACBench Evaluation Module - Handles XACML policy evaluation
"""

import pandas


def load_xacml_policies(csv_path: str):
    """
    Load XACML policies from CSV file.

    Args:
        csv_path: Path to the CSV file containing XACML policies

    Returns:
        pandas.DataFrame: DataFrame containing the policies
    """
    return pandas.read_csv(csv_path)


if __name__ == "__main__":
    df = load_xacml_policies(
        "datasets/xacml/xacBench-datasets/xacml-policies/xacml3_3.csv"
    )
    print(df.describe())
