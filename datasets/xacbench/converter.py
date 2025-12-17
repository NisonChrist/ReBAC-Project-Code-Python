import csv
import os
from pathlib import Path


def extract_policies_to_csv(xml_file_path, output_csv_path):
    """
    Extract all Policy elements from an XACML file and save them to a CSV file.

    Args:
        xml_file_path: Path to the input XACML file
        output_csv_path: Path to the output CSV file
    """
    # Read the XML file as text
    with open(xml_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all Policy elements using string manipulation
    policy_data = []
    start_tag = "<Policy "
    end_tag = "</Policy>"

    start_pos = 0
    while True:
        # Find the next Policy start
        policy_start = content.find(start_tag, start_pos)
        if policy_start == -1:
            break

        # Find the corresponding Policy end
        policy_end = content.find(end_tag, policy_start)
        if policy_end == -1:
            break

        # Extract the complete Policy element
        policy_str = content[policy_start : policy_end + len(end_tag)]
        policy_data.append({"xacml": policy_str})

        # Move past this policy
        start_pos = policy_end + len(end_tag)

    # Write to CSV file
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["xacml"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(policy_data)

    print(f"Extracted {len(policy_data)} policies from {xml_file_path}")
    print(f"Saved to {output_csv_path}")


if __name__ == "__main__":
    # Input and output file paths
    script_dir = Path(__file__).parent.absolute()
    # print(f"Script directory: {script_dir}")
    input_dir = script_dir
    output_dir = script_dir / "xacml-policies"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".xml"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(
                output_dir, filename.replace(".xml", ".csv")
            )
            extract_policies_to_csv(input_path, output_path)

    print("Extraction completed for all files in the directory.")
