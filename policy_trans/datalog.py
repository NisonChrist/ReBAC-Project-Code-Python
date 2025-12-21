import json
from .policy import Policy
from .carminati import Carminati
from .cheng import Cheng
from .crampton import Crampton
from .fong import Fong


class Datalog(Policy):
    def __init__(self, datalog_str: str):
        self._subjects = json.loads(datalog_str).get("subjects", "")
        self._objects = json.loads(datalog_str).get("objects", "")
        self._relationships = json.loads(datalog_str).get("relationships", "")
        self._actions = json.loads(datalog_str).get("actions", "")

    def specifications(self) -> dict[str, str]:
        return {
            "subjects": self._subjects,
            "objects": self._objects,
            "relationships": self._relationships,
            "actions": self._actions,
        }

    def translate2carminati(self) -> Carminati | None:
        pass

    def translate2fong(self) -> Fong | None:
        pass

    def translate2cheng(self) -> Cheng | None:
        pass

    def translate2crampton(self) -> Crampton | None:
        pass

    def get_subjects(self) -> str:
        return self._subjects

    def get_objects(self) -> str:
        return self._objects

    def get_relationships(self) -> str:
        return self._relationships

    def get_actions(self) -> str:
        return self._actions
