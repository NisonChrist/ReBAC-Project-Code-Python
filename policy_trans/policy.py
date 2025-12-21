from abc import ABC, abstractmethod
from typing import Any


class Policy(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def specifications(self) -> Any:
        pass
