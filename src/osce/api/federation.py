from dataclasses import dataclass

@dataclass
class FederatedNode:
    """Minimal representation of a federated node."""
    node_id: str
    address: str
