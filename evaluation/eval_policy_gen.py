import pandas as pd
from typing import cast
from pathlib import Path
import json

gen_ouputs_nl_path = Path(__file__).parent.parent / "_gen_outputs/nl/"
gen_ouputs_xacml_path = Path(__file__).parent.parent / "_gen_outputs/xacml/"

nl_generated_files = list(gen_ouputs_nl_path.glob("*.xlsx"))
xacml_generated_files = list(gen_ouputs_xacml_path.glob("*.xlsx"))

# Use a dictionary to store processed DataFrames
nl_processed_dfs: dict[str, pd.DataFrame] = {}
xacml_processed_dfs: dict[str, pd.DataFrame] = {}

print("NL Generated Policy Files:")
for generated_file in nl_generated_files:
    print(f"- {generated_file.name}")
    df = pd.read_excel(generated_file)
    # print(df.head())
    # print("\n")

    df.insert(3, "datalog_subjects", "")
    df.insert(4, "datalog_objects", "")
    df.insert(5, "datalog_relationships", "")
    df.insert(6, "datalog_actions", "")
    df.insert(7, "success", "")

    for index, row in df.iterrows():
        generated_datalog = df.at[cast(int, index), "generated_datalog"]
        print(f"Record {index} Generated Datalog Policy:\n{generated_datalog}\n")
        try:
            datalog_obj = json.loads(str(generated_datalog))
            # print("Datalog Policy as Object:")
            # print(json.dumps(datalog_obj, indent=4))
            datalog_subjects = datalog_obj.get("datalog_subjects", [])
            datalog_objects = datalog_obj.get("datalog_objects", [])
            datalog_relationships = datalog_obj.get("datalog_relationships", [])
            datalog_actions = datalog_obj.get("datalog_actions", [])
            if (
                datalog_subjects
                or datalog_objects
                or datalog_relationships
                or datalog_actions
            ):
                print("Extracted Components:")
                print(f"- Subjects: {datalog_subjects}")
                print(f"- Objects: {datalog_objects}")
                print(f"- Relationships: {datalog_relationships}")
                print(f"- Actions: {datalog_actions}")
                df.at[cast(int, index), "datalog_subjects"] = datalog_subjects
                df.at[cast(int, index), "datalog_objects"] = datalog_objects
                df.at[cast(int, index), "datalog_relationships"] = datalog_relationships
                df.at[cast(int, index), "datalog_actions"] = datalog_actions
                df.at[cast(int, index), "success"] = 1
            else:
                print("No components extracted from the Datalog policy.")
                df.at[cast(int, index), "success"] = 0
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for record {index}: {e}")
    # Save the processed DataFrame to the dictionary
    nl_processed_dfs[generated_file.name] = df
    print("=====================================\n")

print("XACML Generated Policy Files:")
for generated_file in xacml_generated_files:
    print(f"- {generated_file.name}")
    df = pd.read_excel(generated_file)
    # print(df.head())
    # print("\n")

    df.insert(3, "datalog_subjects", "")
    df.insert(4, "datalog_objects", "")
    df.insert(5, "datalog_relationships", "")
    df.insert(6, "datalog_actions", "")
    df.insert(7, "success", "")

    for index, row in df.iterrows():
        generated_datalog = df.at[cast(int, index), "generated_datalog"]
        print(f"Record {index} Generated Datalog Policy:\n{generated_datalog}\n")
        try:
            datalog_obj = json.loads(str(generated_datalog))
            # print("Datalog Policy as Object:")
            # print(json.dumps(datalog_obj, indent=4))
            datalog_subjects = datalog_obj.get("datalog_subjects", [])
            datalog_objects = datalog_obj.get("datalog_objects", [])
            datalog_relationships = datalog_obj.get("datalog_relationships", [])
            datalog_actions = datalog_obj.get("datalog_actions", [])
            if (
                datalog_subjects
                or datalog_objects
                or datalog_relationships
                or datalog_actions
            ):
                print("Extracted Components:")
                print(f"- Subjects: {datalog_subjects}")
                print(f"- Objects: {datalog_objects}")
                print(f"- Relationships: {datalog_relationships}")
                print(f"- Actions: {datalog_actions}")
                df.at[cast(int, index), "datalog_subjects"] = datalog_subjects
                df.at[cast(int, index), "datalog_objects"] = datalog_objects
                df.at[cast(int, index), "datalog_relationships"] = datalog_relationships
                df.at[cast(int, index), "datalog_actions"] = datalog_actions
                df.at[cast(int, index), "success"] = 1
            else:
                print("No components extracted from the Datalog policy.")
                df.at[cast(int, index), "success"] = 0
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for record {index}: {e}")
    # Save the processed DataFrame to the dictionary
    xacml_processed_dfs[generated_file.name] = df
    print("=====================================\n")

# Get the number of successfully processed policies
for file_name, df in nl_processed_dfs.items():
    success_count = (df["success"] == 1).sum()
    total_count = len(df)
    gen_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    print(
        f"File: {file_name} - Successfully Generated Policies: {success_count}/{total_count} ({gen_rate:.2f}%)"
    )

# Get the number of successfully processed policies
for file_name, df in xacml_processed_dfs.items():
    success_count = (df["success"] == 1).sum()
    total_count = len(df)
    gen_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    print(
        f"File: {file_name} - Successfully Generated Policies: {success_count}/{total_count} ({gen_rate:.2f}%)"
    )


class GenRate:
    def __init__(self, file_name: str, success_count: int, total_count: int):
        self.file_name = file_name
        self.success_count = success_count
        self.total_count = total_count
        self.gen_rate = (success_count / total_count) * 100 if total_count > 0 else 0

    def export_csv(self, output_path: str):
        df = pd.DataFrame(
            {
                "file_name": [self.file_name],
                "success_count": [self.success_count],
                "total_count": [self.total_count],
                "gen_rate": [self.gen_rate],
            }
        )
        df.to_csv(output_path, index=False)
        return df

    def __str__(self):
        return f"File: {self.file_name} - Successfully Generated Policies: {self.success_count}/{self.total_count} ({self.gen_rate:.2f}%)"
