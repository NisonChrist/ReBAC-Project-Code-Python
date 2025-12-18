"""
Main entry point for policy generation system
"""

from pathlib import Path
from policy_gen.llm import LLM, Prompt
from datasets import DatasetReader


def main():
    dr = DatasetReader()

    litroacp_path = Path(__file__).parent / "datasets" / "litroacp"
    print(f"Loading datasets from: {litroacp_path}")
    datasets = dr.load_datasets(litroacp_path)
    print(f"Loaded datasets: {list(datasets.keys())}")

    xacbench_path = Path(__file__).parent / "datasets" / "xacbench"
    print(f"Loading XACBench datasets from: {xacbench_path}")
    datasets = dr.load_datasets(xacbench_path)
    print(f"Loaded XACBench datasets: {list(datasets.keys())}")

    """Main function to run policy generation"""
    prompt_list = [
        Prompt(
            system="You are a helpful assistant. Help me solve the following problem. The answer should be in JSON format.",
            user="1+1=?",
            template="sample",
        )
    ]
    deepseek = LLM(prompt_list=prompt_list)
    output = deepseek.generate()
    print(output)


if __name__ == "__main__":
    main()
