from pathlib import Path
from typing import Any, Callable
import logging
import os
import re
import pandas as pd
from pandas import DataFrame

type DatasetsDict = dict[str, DataFrame]
type IsSingleton = bool


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def iter_dir(path: Path) -> filter:
    def is_jsonl(file: Path) -> bool:
        if str(file).endswith(".jsonl"):
            logger.info(f"{file}")
            return True
        else:
            logger.warning(f"{file}, skipping")
            return False

    return filter(is_jsonl, path.iterdir())


class Dataset:
    def __init__(self, name: str, path: Path) -> None:
        self._name: str = name
        self._path: Path = path
        self._data: DataFrame = pd.read_json(str(path), lines=True)

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def data(self) -> DataFrame:
        return self._data

    def __str__(self) -> str:
        return f"\nname: {self._name}\npath: {self._path}\ndata:\n{self._data.head()}"


class DatasetLoader:
    def __init__(self, nl_dir: Path, xacml_dir: Path) -> None:
        self.nl_dir: Path = nl_dir
        self.xacml_dir: Path = xacml_dir
        self.nl_acp_datasets: DatasetsDict | None = None
        self.xacml_acp_datasets: DatasetsDict | None = None

    def load(self) -> tuple[DatasetsDict, DatasetsDict]:
        return (self._load_nl_acp(), self._load_xacml_acp())

    def _load_nl_acp(self) -> DatasetsDict:
        datasets: DatasetsDict = {}
        for file_name in sorted(os.listdir(self.nl_dir)):
            file_path = self.nl_dir / file_name
            try:
                if file_name.endswith(".jsonl"):
                    df = pd.read_json(str(file_path), lines=True)
                    datasets[file_name] = df
                    logging.info(f"Loaded {file_name} with shape: {df.shape}")
                else:
                    logging.warning(
                        f"Unsupported file format for {file_name}, skipping."
                    )
                    continue
            except Exception as e:
                logging.error(f"Error loading {file_name}: {e}")
        self.nl_acp_datasets = datasets
        return self.nl_acp_datasets

    def _load_xacml_acp(self) -> DatasetsDict:
        datasets: DatasetsDict = {}
        for file_name in sorted(os.listdir(self.xacml_dir)):
            file_path = self.xacml_dir / file_name
            try:
                if file_name.endswith(".xml"):
                    with open(file_path, "r", encoding="utf-8") as file:
                        policy_pattern = re.compile(
                            r"<Policy\s[^>]*>[\s\S]*?<\/Policy>"
                        )
                        xacml_content = file.read()
                        policies = policy_pattern.findall(xacml_content)
                        datasets[file_name] = pd.DataFrame({"policy": policies})
                        logging.info(
                            f"Loaded {file_name} with {len(policies)} policies."
                        )
                else:
                    logging.warning(
                        f"Unsupported file format for {file_name}, skipping."
                    )
                    continue
            except Exception as e:
                logging.error(f"Error loading {file_name}: {e}")
        self.xacml_acp_datasets = datasets
        return self.xacml_acp_datasets


class DatasetTransformer:
    def transform(self):
        return


class PolicyGenerator:
    def generate(self):
        return


class PolicyTranslator:
    def translate(self):
        return


class Workflow:
    def __init__(
        self,
        dataset_loader: DatasetLoader,
        dataset_transformer: DatasetTransformer,
        policy_generator: PolicyGenerator,
        policy_translator: PolicyTranslator,
    ) -> None:
        self.loader = dataset_loader
        self.transformer = dataset_transformer
        self.generator = policy_generator
        self.translator = policy_translator

    def run(self) -> None:
        print("run")


class Container:
    def __init__(self) -> None:
        self._providers: dict[str, tuple[Callable[[], Any], IsSingleton]] = {}
        self._singletons: dict[str, Any] = {}

    def register(
        self, name: str, provider: Callable[[], Any], singleton: IsSingleton = False
    ) -> None:
        self._providers[name] = (provider, singleton)

    def resolve(self, name: str) -> Any:
        if name in self._singletons:
            return self._singletons[name]
        if name not in self._providers:
            raise ValueError(f"No provider registered for '{name}'")
        provider, singleton = self._providers[name]
        instance = provider()
        if singleton:
            self._singletons[name] = instance
        return instance


# workflow = Workflow(
#     dataset_loader=DatasetLoader(),
#     dataset_transformer=DatasetTransformer(),
#     policy_generator=PolicyGenerator(),
#     policy_translator=PolicyTranslator(),
# )
#
# workflow.run()
