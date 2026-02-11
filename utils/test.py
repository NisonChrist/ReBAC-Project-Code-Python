from pathlib import Path
from workflow import Dataset
from workflow import iter_dir

# from workflow import DatasetLoader
from workflow import DatasetsDict


def main() -> None:
    # p = Path(__file__).parent.parent / "datasets" / "litroacp" / "acre_acp.jsonl"
    # d = Dataset(name="acre_acp", path=p)
    # print(d)
    pp = Path(__file__).parent.parent / "datasets" / "litroacp"
    # print(list(pp.glob("*.jsonl")))
    f = iter_dir(pp)
    for i in f:
        print(i)


if __name__ == "__main__":
    main()
