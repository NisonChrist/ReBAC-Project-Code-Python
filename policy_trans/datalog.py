import json
import re
from policy import Policy
from carminati import Carminati
from cheng import (
    Cheng,
    Connective,
    StartingNode,
    TypeExp,
    PathSpec,
    PathSpecExp,
    PathRule,
    GraphRule,
    AccessingUserPolicy,
    TargetUserPolicy,
    TargetResourcePolicy,
    SystemPolicyForUser,
    SystemPolicyForResource,
)
from crampton import Crampton
from fong import Fong


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
        """
        Translate Datalog policy to Cheng's UURAC model.

        Cheng's UURAC model uses path expressions to represent relationship patterns
        between users. The translation maps:
        - Datalog relationships -> Path expressions with hop counts
        - Datalog actions -> UURAC policies (AUP, TUP, TRP, or System policies)
        - Negation in Datalog -> Negated PathSpecExp

        Returns:
            Cheng: The translated UURAC policy, or None if translation fails
        """
        try:
            # Extract relationship types from Datalog
            relationship_types = self._extract_relationship_types()

            # Parse action rules and generate UURAC policies
            accessing_user_policies = []
            target_user_policies = []
            target_resource_policies = []
            system_policies_user = []
            system_policies_resource = []

            # Parse action rules
            action_rules = self._parse_action_rules()

            for rule in action_rules:
                policy = self._convert_rule_to_cheng_policy(rule, relationship_types)
                if policy:
                    if isinstance(policy, AccessingUserPolicy):
                        accessing_user_policies.append(policy)
                    elif isinstance(policy, TargetUserPolicy):
                        target_user_policies.append(policy)
                    elif isinstance(policy, TargetResourcePolicy):
                        target_resource_policies.append(policy)
                    elif isinstance(policy, SystemPolicyForUser):
                        system_policies_user.append(policy)
                    elif isinstance(policy, SystemPolicyForResource):
                        system_policies_resource.append(policy)

            return Cheng(
                relationship_types=relationship_types,
                accessing_user_policies=accessing_user_policies,
                target_user_policies=target_user_policies,
                target_resource_policies=target_resource_policies,
                system_policies_user=system_policies_user,
                system_policies_resource=system_policies_resource,
            )
        except Exception as e:
            print(f"Translation to Cheng UURAC failed: {e}")
            return None

    def _extract_relationship_types(self) -> set[str]:
        """
        Extract relationship types (Σ) from Datalog relationships.
        For each relationship type σ, also includes its inverse σ^(-1).
        """
        relationship_types = set()

        # Parse relationship definitions
        # Format: "rel_name(args) :- body." or just "rel_name(args)."
        rel_pattern = r"(\w+)\s*\([^)]+\)"

        matches = re.findall(rel_pattern, self._relationships)
        for rel_name in matches:
            # Skip type predicates (capitalized)
            if not rel_name[0].isupper():
                relationship_types.add(rel_name)
                relationship_types.add(f"{rel_name}^(-1)")

        return relationship_types

    def _parse_action_rules(self) -> list[dict]:
        """
        Parse Datalog action rules into structured format.

        Returns list of dicts with:
        - 'head': the action predicate
        - 'head_args': arguments of the head
        - 'body': list of body predicates
        - 'negations': list of negated predicates
        """
        rules = []

        # Split action string into individual rules
        # Format: "action(args) :- body1, body2, not body3."
        action_str = self._actions.strip()
        if not action_str:
            return rules

        # Split by '.' but keep track of complete rules
        rule_strs = [r.strip() for r in action_str.split(".") if r.strip()]

        for rule_str in rule_strs:
            if ":-" not in rule_str:
                continue

            # Split into head and body
            parts = rule_str.split(":-")
            if len(parts) != 2:
                continue

            head_str = parts[0].strip()
            body_str = parts[1].strip()

            # Parse head: action_name(arg1, arg2, ...)
            head_match = re.match(r"(\w+)\s*\(([^)]*)\)", head_str)
            if not head_match:
                continue

            head_name = head_match.group(1)
            head_args = [a.strip() for a in head_match.group(2).split(",")]

            # Parse body predicates
            body_predicates = []
            negated_predicates = []

            # Split body by commas (careful with nested parentheses)
            body_parts = self._split_body(body_str)

            for pred_str in body_parts:
                pred_str = pred_str.strip()
                if pred_str.startswith("not "):
                    # Negated predicate
                    pred_str = pred_str[4:].strip()
                    pred_match = re.match(r"(\w+)\s*\(([^)]*)\)", pred_str)
                    if pred_match:
                        negated_predicates.append(
                            {
                                "name": pred_match.group(1),
                                "args": [
                                    a.strip() for a in pred_match.group(2).split(",")
                                ],
                            }
                        )
                else:
                    # Positive predicate
                    pred_match = re.match(r"(\w+)\s*\(([^)]*)\)", pred_str)
                    if pred_match:
                        body_predicates.append(
                            {
                                "name": pred_match.group(1),
                                "args": [
                                    a.strip() for a in pred_match.group(2).split(",")
                                ],
                            }
                        )

            rules.append(
                {
                    "head": head_name,
                    "head_args": head_args,
                    "body": body_predicates,
                    "negations": negated_predicates,
                }
            )

        return rules

    def _split_body(self, body_str: str) -> list[str]:
        """Split body string by commas, respecting parentheses."""
        parts = []
        current = []
        depth = 0

        for char in body_str:
            if char == "(":
                depth += 1
                current.append(char)
            elif char == ")":
                depth -= 1
                current.append(char)
            elif char == "," and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)

        if current:
            parts.append("".join(current))

        return parts

    def _convert_rule_to_cheng_policy(
        self, rule: dict, relationship_types: set[str]
    ) -> (
        AccessingUserPolicy
        | TargetUserPolicy
        | TargetResourcePolicy
        | SystemPolicyForUser
        | SystemPolicyForResource
        | None
    ):
        """
        Convert a parsed Datalog rule to appropriate Cheng UURAC policy.

        Determines policy type based on:
        - If head involves user-to-user action -> AUP or TUP
        - If head involves user-to-resource action -> TRP
        - System-wide rules -> SP-User or SP-Resource
        """
        action_name = rule["head"]
        head_args = rule["head_args"]
        body = rule["body"]
        negations = rule["negations"]

        # Identify entity types from body predicates
        entity_types = {}
        for pred in body:
            # Type predicates are usually capitalized (e.g., Patient(P), User(U))
            if pred["name"][0].isupper() and len(pred["args"]) == 1:
                var = pred["args"][0]
                entity_types[var] = pred["name"]

        # Build path expressions from relationship predicates
        path_expressions = []
        for pred in body:
            # Relationship predicates are lowercase
            if not pred["name"][0].isupper():
                path_expressions.append(pred)

        # Build negated path expressions
        negated_expressions = []
        for pred in negations:
            if not pred["name"][0].isupper():
                negated_expressions.append(pred)

        # Determine the type of policy based on arguments
        # Convention: first arg is typically the subject (accessing user)
        # second arg is typically the target (user or resource)

        if len(head_args) >= 2:
            subject_var = head_args[0]
            target_var = head_args[1] if len(head_args) > 1 else None
            resource_var = head_args[2] if len(head_args) > 2 else None

            _ = entity_types.get(subject_var, "User")  # subject_type for future use
            target_type = entity_types.get(target_var, "User") if target_var else None
            resource_type = (
                entity_types.get(resource_var, "Resource") if resource_var else None
            )

            # Build graph rule
            graph_rule = self._build_graph_rule(
                path_expressions,
                negated_expressions,
                subject_var,
                target_var,
                resource_var,
                entity_types,
            )

            # Determine policy type
            if resource_var and resource_type:
                # User-to-Resource access: Target Resource Policy
                return TargetResourcePolicy(
                    action_inverse=action_name,
                    resource=resource_type,
                    graph_rule=graph_rule,
                )
            elif target_var and target_type:
                # Check if this is user-to-user interaction
                # If subject is accessing, it's AUP; if target perspective, it's TUP
                # Default to Accessing User Policy for action definitions
                return AccessingUserPolicy(action=action_name, graph_rule=graph_rule)

        return None

    def _build_graph_rule(
        self,
        path_expressions: list[dict],
        negated_expressions: list[dict],
        subject_var: str,
        target_var: str | None,
        resource_var: str | None,
        entity_types: dict[str, str],
    ) -> GraphRule:
        """
        Build a GraphRule from path expressions.

        Maps Datalog relationships to path patterns:
        - rel(X, Y) -> path from X to Y with relationship type 'rel'
        - Multiple relationships -> path composition or conjunction
        """
        # Determine starting node
        starting_node = StartingNode.ACCESSING_USER

        # Build PathSpecExps
        path_spec_exprs = []

        # Process positive path expressions
        for expr in path_expressions:
            rel_name = expr["name"]
            # args = expr['args']  # Can be used for variable binding analysis

            # Create TypeExp for this relationship
            type_exp = TypeExp(type_specifier=rel_name)

            # Create PathSpec (hop count = 1 for direct relationship)
            path_spec = PathSpec(path=[type_exp], hop_count=1)

            # Create PathSpecExp (not negated)
            path_spec_exp = PathSpecExp(path_spec=path_spec, negated=False)
            path_spec_exprs.append((path_spec_exp, None))

        # Process negated path expressions
        for expr in negated_expressions:
            rel_name = expr["name"]

            type_exp = TypeExp(type_specifier=rel_name)
            path_spec = PathSpec(path=[type_exp], hop_count=1)

            # Create negated PathSpecExp
            path_spec_exp = PathSpecExp(path_spec=path_spec, negated=True)
            path_spec_exprs.append((path_spec_exp, None))

        # Connect expressions with AND connective
        if len(path_spec_exprs) > 1:
            connected_exprs = []
            for i, (expr, _) in enumerate(path_spec_exprs):
                if i < len(path_spec_exprs) - 1:
                    connected_exprs.append((expr, Connective.AND))
                else:
                    connected_exprs.append((expr, None))
            path_spec_exprs = connected_exprs

        # If no path expressions, create empty path rule
        if not path_spec_exprs:
            empty_path_spec = PathSpec(path=None, hop_count=0)
            path_spec_exprs = [(PathSpecExp(path_spec=empty_path_spec), None)]

        # Type cast for PathRule constructor
        expressions: list[tuple[PathSpecExp, Connective | None]] = path_spec_exprs  # type: ignore
        path_rule = PathRule(expressions=expressions)

        return GraphRule(starting_node=starting_node, path_rule=path_rule)

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

    def __str__(self) -> str:
        return (
            f"Datalog Policy:\n"
            f"Subjects: {self._subjects}\n"
            f"Objects: {self._objects}\n"
            f"Relationships: {self._relationships}\n"
            f"Actions: {self._actions}\n"
        )
