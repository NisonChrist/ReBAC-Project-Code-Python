from policy import Policy
from typing import Any
from enum import Enum
from dataclasses import dataclass


class Wildcard(Enum):
    """Wildcards for path expressions: *, +, ?"""

    STAR = "*"  # 0 or more
    PLUS = "+"  # 1 or more
    QUESTION = "?"  # 0 or 1


class Connective(Enum):
    """Logical connectives for path rules"""

    AND = "and"
    OR = "or"


class StartingNode(Enum):
    """Starting node types in graph rules"""

    ACCESSING_USER = "u_a"  # Accessing user
    TARGET_USER = "u_t"  # Target user
    CONTROLLING_USER = "u_c"  # Controlling user


@dataclass
class TypeExp:
    """Type expression: <TypeSpecifier> [<Wildcard>]"""

    type_specifier: str  # relationship type (e.g., "friend", "friend^-1")
    wildcard: Wildcard | None = None

    def __str__(self) -> str:
        if self.wildcard:
            return f"{self.type_specifier}{self.wildcard.value}"
        return self.type_specifier


@dataclass
class PathSpec:
    """Path specification: (<Path>, <HopCount>) | (∅, <HopCount>)"""

    path: list[TypeExp] | None  # None represents empty set
    hop_count: int

    def __str__(self) -> str:
        if self.path is None:
            return f"(∅, {self.hop_count})"
        path_str = "".join(str(t) for t in self.path)
        return f"({path_str}, {self.hop_count})"


@dataclass
class PathSpecExp:
    """Path specification expression: <PathSpec> | NOT <PathSpec>"""

    path_spec: PathSpec
    negated: bool = False

    def __str__(self) -> str:
        if self.negated:
            return f"¬{self.path_spec}"
        return str(self.path_spec)


@dataclass
class PathRule:
    """Path rule: <PathSpecExp> | <PathSpecExp> <Connective> <PathRule>"""

    expressions: list[tuple[PathSpecExp, Connective | None]]

    def __str__(self) -> str:
        result = []
        for expr, conn in self.expressions:
            result.append(str(expr))
            if conn:
                result.append(f" {conn.value} ")
        return "".join(result)


@dataclass
class GraphRule:
    """Graph rule: (<StartingNode>, <PathRule>)"""

    starting_node: StartingNode
    path_rule: PathRule

    def __str__(self) -> str:
        return f"({self.starting_node.value}, {self.path_rule})"


@dataclass
class AccessingUserPolicy:
    """Accessing User Policy: <action, (start, path rule)>"""

    action: str
    graph_rule: GraphRule

    def __str__(self) -> str:
        return f"⟨{self.action}, {self.graph_rule}⟩"


@dataclass
class TargetUserPolicy:
    """Target User Policy: <action^-1, (start, path rule)>"""

    action_inverse: str
    graph_rule: GraphRule

    def __str__(self) -> str:
        return f"⟨{self.action_inverse}⁻¹, {self.graph_rule}⟩"


@dataclass
class TargetResourcePolicy:
    """Target Resource Policy: <action^-1, r_t, (start, path rule)>"""

    action_inverse: str
    resource: str
    graph_rule: GraphRule

    def __str__(self) -> str:
        return f"⟨{self.action_inverse}⁻¹, {self.resource}, {self.graph_rule}⟩"


@dataclass
class SystemPolicyForUser:
    """System Policy for User: <action, (start, path rule)>"""

    action: str
    graph_rule: GraphRule

    def __str__(self) -> str:
        return f"⟨{self.action}, {self.graph_rule}⟩"


@dataclass
class SystemPolicyForResource:
    """System Policy for Resource: <action^-1, r.type, (start, path rule)>"""

    action_inverse: str
    resource_type: str
    graph_rule: GraphRule

    def __str__(self) -> str:
        return f"⟨{self.action_inverse}⁻¹, {self.resource_type}, {self.graph_rule}⟩"


class Cheng(Policy):
    """
    Cheng et al.'s UURAC (User-to-User Relationship-based Access Control) Model

    Policy types:
    - Accessing User Policy (AUP): outgoing action policies
    - Target User Policy (TUP): incoming action policies for users
    - Target Resource Policy (TRP): incoming action policies for resources
    - System Policy for User (SP-User): system-wide policies for users
    - System Policy for Resource (SP-Resource): system-wide policies for resources
    """

    def __init__(
        self,
        relationship_types: set[str] | None = None,
        accessing_user_policies: list[AccessingUserPolicy] | None = None,
        target_user_policies: list[TargetUserPolicy] | None = None,
        target_resource_policies: list[TargetResourcePolicy] | None = None,
        system_policies_user: list[SystemPolicyForUser] | None = None,
        system_policies_resource: list[SystemPolicyForResource] | None = None,
    ):
        self._relationship_types = relationship_types or set()
        self._accessing_user_policies = accessing_user_policies or []
        self._target_user_policies = target_user_policies or []
        self._target_resource_policies = target_resource_policies or []
        self._system_policies_user = system_policies_user or []
        self._system_policies_resource = system_policies_resource or []

    def specifications(self) -> dict[str, Any]:
        return {
            "relationship_types": self._relationship_types,
            "accessing_user_policies": self._accessing_user_policies,
            "target_user_policies": self._target_user_policies,
            "target_resource_policies": self._target_resource_policies,
            "system_policies_user": self._system_policies_user,
            "system_policies_resource": self._system_policies_resource,
        }

    @property
    def relationship_types(self) -> set[str]:
        """Σ = {σ₁, σ₂, ..., σₙ, σ₁⁻¹, σ₂⁻¹, ..., σₙ⁻¹}"""
        return self._relationship_types

    @property
    def accessing_user_policies(self) -> list[AccessingUserPolicy]:
        return self._accessing_user_policies

    @property
    def target_user_policies(self) -> list[TargetUserPolicy]:
        return self._target_user_policies

    @property
    def target_resource_policies(self) -> list[TargetResourcePolicy]:
        return self._target_resource_policies

    @property
    def system_policies_user(self) -> list[SystemPolicyForUser]:
        return self._system_policies_user

    @property
    def system_policies_resource(self) -> list[SystemPolicyForResource]:
        return self._system_policies_resource

    def __str__(self) -> str:
        lines = ["Cheng UURAC Policy:"]
        lines.append(f"  Relationship Types (Σ): {self._relationship_types}")

        if self._accessing_user_policies:
            lines.append("  Accessing User Policies (AUP):")
            for p in self._accessing_user_policies:
                lines.append(f"    {p}")

        if self._target_user_policies:
            lines.append("  Target User Policies (TUP):")
            for p in self._target_user_policies:
                lines.append(f"    {p}")

        if self._target_resource_policies:
            lines.append("  Target Resource Policies (TRP):")
            for p in self._target_resource_policies:
                lines.append(f"    {p}")

        if self._system_policies_user:
            lines.append("  System Policies for User (SP-User):")
            for p in self._system_policies_user:
                lines.append(f"    {p}")

        if self._system_policies_resource:
            lines.append("  System Policies for Resource (SP-Resource):")
            for p in self._system_policies_resource:
                lines.append(f"    {p}")

        return "\n".join(lines)
