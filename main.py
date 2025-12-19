from pathlib import Path
from typing import cast
from pandas import DataFrame
from policy_gen.llm import LLM, Prompt
from datasets import DatasetReader


def process_datasets() -> tuple[dict[str, DataFrame], dict[str, DataFrame]]:
    """Process datasets for policy generation"""
    dr = DatasetReader()

    litroacp_path = Path(__file__).parent / "datasets" / "litroacp"
    print(f"Loading datasets from: {litroacp_path}")
    nl_datasets = dr.load_datasets(litroacp_path)
    print(f"Loaded datasets: {list(nl_datasets.keys())}")

    xacbench_path = Path(__file__).parent / "datasets" / "xacbench"
    print(f"Loading XACBench datasets from: {xacbench_path}")
    xacml_datasets = dr.load_datasets(xacbench_path)
    print(f"Loaded XACBench datasets: {list(xacml_datasets.keys())}")

    return nl_datasets, xacml_datasets


def generate_policies(
    nl_datasets: dict[str, DataFrame],
    xacml_datasets: dict[str, DataFrame],
):
    """
    Generate policies using LLM based on NL datasets and XACML datasets
    """

    """Load system message template"""
    system_msg_path = Path(__file__).parent / "policy_gen" / "llm" / "system_msg.txt"
    system_msg = ""
    with open(system_msg_path, "r") as f:
        system_msg = f.read()
    print(f"Loaded system message from: {system_msg_path}")
    print(system_msg)
    """Generate policies for NL datasets"""
    for nl_dataset_name, nl_dataset in nl_datasets.items():
        print(
            f"Processing NL dataset: {nl_dataset_name} with {len(nl_dataset)} records"
        )
        nl_dataset_processed = nl_dataset.drop(
            ["id", "entities", "relations", "Comments"], axis="columns", inplace=False
        )
        nl_dataset_processed.rename(columns={"text": "user_message"}, inplace=True)
        nl_dataset_processed.insert(
            nl_dataset_processed.shape[1],
            "system_message",
            system_msg,
        )
        nl_dataset_processed.insert(
            nl_dataset_processed.shape[1],
            "generated_datalog",
            "",
        )
        print(nl_dataset_processed.head())

        llm = LLM()
        for index, row in nl_dataset_processed.iterrows():
            prompt = Prompt(
                system=row["system_message"],
                user=row["user_message"],
            )
            output = llm.generate(prompt)
            print(f"Generated policy for record {index}:\n{output}")
            nl_dataset_processed.loc[cast(int, index), "generated_datalog"] = output
        nl_datasets[nl_dataset_name] = nl_dataset_processed
    """Generate policies for XACML datasets"""
    for xacml_dataset_name, xacml_dataset in xacml_datasets.items():
        print(
            f"Processing XACML dataset: {xacml_dataset_name} with {len(xacml_dataset)} records"
        )
        xacml_dataset_processed = xacml_dataset.drop([], axis="columns", inplace=False)
        xacml_dataset_processed.rename(columns={"policy": "user_message"}, inplace=True)
        xacml_dataset_processed.insert(
            xacml_dataset_processed.shape[1],
            "system_message",
            system_msg,
        )
        xacml_dataset_processed.insert(
            xacml_dataset_processed.shape[1],
            "generated_datalog",
            "",
        )
        print(xacml_dataset_processed.head())

        llm = LLM()
        for index, row in xacml_dataset_processed.iterrows():
            prompt = Prompt(
                system=row["system_message"],
                user=row["user_message"],
            )
            output = llm.generate(prompt)
            print(f"Generated policy for record {index}:\n{output}")
            xacml_dataset_processed.loc[cast(int, index), "generated_datalog"] = output
        xacml_datasets[xacml_dataset_name] = xacml_dataset_processed

    # Save generated datasets to excel files
    for nl_dataset_name, nl_dataset in nl_datasets.items():
        output_path = f"_gen_outputs/nl/{nl_dataset_name}.xlsx"
        nl_dataset.to_excel(output_path, index=False)
        print(f"Saved generated NL dataset to: {output_path}")
    for xacml_dataset_name, xacml_dataset in xacml_datasets.items():
        output_path = f"_gen_outputs/xacml/{xacml_dataset_name}.xlsx"
        xacml_dataset.to_excel(output_path, index=False)
        print(f"Saved generated XACML dataset to: {output_path}")

    return nl_datasets, xacml_datasets


def translate_policies():
    """Translate policies using tailored algorithms"""
    pass


def main():
    # Oh god! These are dirty variables ...
    nl_datasets, xacml_datasets = process_datasets()
    nl_gen_results, xacml_gen_results = generate_policies(nl_datasets, xacml_datasets)
    print("NL Generated Results:")
    for name, df in nl_gen_results.items():
        print(f"Dataset: {name}")
        print(df.head())
    print("XACML Generated Results:")
    for name, df in xacml_gen_results.items():
        print(f"Dataset: {name}")
        print(df.head())
    translate_policies()


if __name__ == "__main__":
    main()
