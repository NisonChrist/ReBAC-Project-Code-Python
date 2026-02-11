from enum import Enum


class Wildcard(Enum):
    STAR = "*"
    PLUS = "+"
    QUESTION = "?"


class Connective(Enum):
    AND = "AND"
    OR = "OR"
