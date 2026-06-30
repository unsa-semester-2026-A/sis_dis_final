"""Financial node type classification."""

import enum


class NodeType(enum.Enum):
    """Classification of financial graph nodes.

    Each type governs the node's accounting behavior:
        ASSET: Real money under control (bank accounts, receivables).
        LIABILITY: Debt obligations (credit lines, loans owed).
        SOURCE: External origin of funds (salary, interest).
        SINK: Final expense destination / budget category.
    """

    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    SOURCE = "SOURCE"
    SINK = "SINK"


__all__ = ["NodeType"]
