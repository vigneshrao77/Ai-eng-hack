from typing import List, Set, Tuple
from app.engines.council.schema import CouncilDecision

VALID_STRATEGIES = {
    "Retire",
    "Retain",
    "Rehost",
    "Relocate",
    "Replatform",
    "Repurchase",
    "Refactor",
}

VALID_PATTERNS = {
    "StranglerFig",
    "EventDriven",
    "CQRS",
    "Serverless",
    "Containerized",
    "ManagedDB",
    "APIGateway",
    "SaaS",
}


class DecisionValidationError(Exception):
    def __init__(self, errors: List[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def validate_decision(
    decision: CouncilDecision, valid_node_ids: Set[str]
) -> Tuple[bool, List[str]]:
    """
    Validates that a CouncilDecision complies strictly with the architectural and
    self-compliance rules:
    1. Strategy is one of the valid 7R strategies.
    2. Effort estimates are non-negative and satisfy optimistic <= likely <= pessimistic.
    3. Confidence is between 0.0 and 1.0.
    4. At least one evidence node ID is provided.
    5. Every evidence node ID strictly exists in the project's knowledge graph.
    """
    errors: List[str] = []

    if decision.strategy not in VALID_STRATEGIES:
        errors.append(f"Invalid strategy '{decision.strategy}'. Must be one of {sorted(VALID_STRATEGIES)}.")

    for pattern in decision.target_pattern:
        if pattern not in VALID_PATTERNS:
            errors.append(f"Invalid target pattern '{pattern}'. Must be one of {sorted(VALID_PATTERNS)}.")

    if not (0.0 <= decision.confidence <= 1.0):
        errors.append(f"Confidence {decision.confidence} out of range [0.0, 1.0].")

    if not decision.rationale or len(decision.rationale.strip()) < 10:
        errors.append("Rationale must be a substantive explanation of at least 10 characters.")

    if len(decision.effort_weeks) != 3:
        errors.append("Effort estimates must be a 3-tuple (optimistic, likely, pessimistic).")
    else:
        opt, likely, pess = decision.effort_weeks
        if opt < 0 or likely < 0 or pess < 0:
            errors.append("Effort estimates must be non-negative numbers.")
        if opt > likely:
            errors.append(f"Optimistic effort ({opt}) cannot exceed likely effort ({likely}).")
        if likely > pess:
            errors.append(f"Likely effort ({likely}) cannot exceed pessimistic effort ({pess}).")

    if not decision.evidence_node_ids:
        errors.append("Council decision must cite at least one evidence_node_id from the knowledge graph.")
    else:
        unknown_nodes = [nid for nid in decision.evidence_node_ids if nid not in valid_node_ids]
        if unknown_nodes:
            errors.append(
                f"Unknown evidence node IDs cited: {unknown_nodes}. All citations must exist in the repository knowledge graph."
            )

    return len(errors) == 0, errors
