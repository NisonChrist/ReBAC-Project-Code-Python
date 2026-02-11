from typing import Protocol, Callable, Any
import json
from pathlib import Path
import os
import re
import logging
import pandas as pd
from pandas import DataFrame

type Data = list[dict[str, Any]]


# === Interfaces ===
class DataLoader(Protocol):
    def load(self) -> Data: ...


class Transformer(Protocol):
    def transform(self, data: Data) -> Data: ...


class Exporter(Protocol):
    def export(self, data: Data) -> None: ...


# === Concrete implementations ===
class InMemoryLoader:
    def load_nl_dataset(self, dir_path: Path) -> dict[str, DataFrame]:
        datasets = {}
        for file_name in sorted(os.listdir(dir_path)):
            file_path = dir_path / file_name
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
        return datasets

    def load_xacml_dataset(self, dir_path: Path) -> dict[str, DataFrame]:
        datasets = {}
        for file_name in sorted(os.listdir(dir_path)):
            file_path = dir_path / file_name
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
        return datasets


class CleanMissingFields:
    def transform(self, data: Data) -> Data:
        return [row for row in data if row["age"] is not None]


class JSONExporter:
    def __init__(self, filename: str):
        self.filename = filename

    def export(self, data: Data) -> None:
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)


# === Pipeline ===
class DataPipeline:
    def __init__(
        self, loader: DataLoader, transformer: Transformer, exporter: Exporter
    ):
        self.loader = loader
        self.transformer = transformer
        self.exporter = exporter

    def run(self) -> None:
        data = self.loader.load()
        clean = self.transformer.transform(data)
        self.exporter.export(clean)


# === Simple DI container ===
class Container:
    def __init__(self) -> None:
        self._providers: dict[str, tuple[Callable[[], Any], bool]] = {}
        self._singletons: dict[str, Any] = {}

    def register(
        self, name: str, provider: Callable[[], Any], singleton: bool = False
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


# === Main runner ===
def main() -> None:
    container = Container()

    container.register("loader", lambda: InMemoryLoader(), singleton=True)
    container.register("transformer", lambda: CleanMissingFields())
    container.register("exporter", lambda: JSONExporter("output.json"))

    container.register(
        "pipeline",
        lambda: DataPipeline(
            loader=container.resolve("loader"),
            transformer=container.resolve("transformer"),
            exporter=container.resolve("exporter"),
        ),
    )

    pipeline: DataPipeline = container.resolve("pipeline")
    pipeline.run()
    print("Pipeline finished. Output written to output.json")


if __name__ == "__main__":
    main()
