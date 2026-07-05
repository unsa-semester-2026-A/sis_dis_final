# pyright: reportUnusedFunction=false
"""REST adapter for the ledger bounded context.

This is a PRIMARY adapter (driving side). It translates HTTP requests
into domain commands/queries and delegates to use case ports.
The domain has zero knowledge of FastAPI, HTTP, or JSON.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.ledger.core.node import Node
from app.ledger.core.node_type import NodeType
from app.ledger.core.vector import Vector
from app.ledger.ports.inbound import (
    BalanceQuery,
    CreateNodeCommand,
    CreateNodePort,
    EmitVectorCommand,
    EmitVectorPort,
    EvaluateBalancePort,
)
from app.shared import DomainError, EntityId, InactiveNodeError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field  # pyright: ignore[reportUnknownVariableType]

# ---------------------------------------------------------------------------
# Request / Response schemas (Pydantic — adapter concern, NOT domain)
# ---------------------------------------------------------------------------


class CreateNodeRequest(BaseModel):
    """HTTP request body for node creation."""

    user_id: UUID
    name: str
    node_type: str
    currency: str


class NodeResponse(BaseModel):
    """HTTP response for a node."""

    id: str
    user_id: str
    name: str
    node_type: str
    currency: str
    is_active: bool


class EmitVectorRequest(BaseModel):
    """HTTP request body for vector emission."""

    source_node_id: UUID
    target_node_id: UUID
    amount: str
    exchange_rate: str = "1.0"
    lineage_token: str | None = None
    transaction_id: UUID | None = None
    tags: dict[str, str] = Field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]
    effective_at: datetime | None = None


class VectorResponse(BaseModel):
    """HTTP response for a vector."""

    id: str
    lineage_token: str
    source_node_id: str
    target_node_id: str
    amount: str
    exchange_rate: str
    effective_at: str
    system_at: str
    transaction_id: str | None
    tags: dict[str, str]


class BalanceResponse(BaseModel):
    """HTTP response for a balance query."""

    amount: str
    currency: str


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------


def _node_to_response(node: Node) -> NodeResponse:
    return NodeResponse(
        id=str(node.id),
        user_id=str(node.user_id),
        name=node.name,
        node_type=node.node_type.value,
        currency=node.currency,
        is_active=node.is_active,
    )


def _vector_to_response(vector: Vector) -> VectorResponse:
    return VectorResponse(
        id=str(vector.id),
        lineage_token=vector.lineage_token,
        source_node_id=str(vector.source_node_id),
        target_node_id=str(vector.target_node_id),
        amount=str(vector.amount),
        exchange_rate=str(vector.exchange_rate),
        effective_at=vector.effective_at.isoformat(),
        system_at=vector.system_at.isoformat(),
        transaction_id=str(vector.transaction_id) if vector.transaction_id else None,
        tags=dict(vector.tags),
    )


# ---------------------------------------------------------------------------
# Router factory (dependency injection at the adapter boundary)
# ---------------------------------------------------------------------------


def create_ledger_router(
    create_node: CreateNodePort,
    emit_vector: EmitVectorPort,
    evaluate_balance: EvaluateBalancePort,
) -> APIRouter:
    """Create the ledger REST router with injected inbound ports.

    Args:
        create_node: Inbound port for node creation.
        emit_vector: Inbound port for vector emission.
        evaluate_balance: Inbound port for balance evaluation.

    Returns:
        APIRouter: A configured FastAPI APIRouter.
    """
    router = APIRouter(tags=["ledger"])

    @router.post("/nodes", response_model=NodeResponse, status_code=201)
    def post_create_node(body: CreateNodeRequest) -> NodeResponse:
        """Create a new financial node."""
        try:
            node_type = NodeType(body.node_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid node_type: {body.node_type}",
            )

        try:
            cmd = CreateNodeCommand(
                user_id=EntityId(body.user_id),
                name=body.name,
                node_type=node_type,
                currency=body.currency,
            )
            node = create_node.execute(cmd)
        except (ValueError, DomainError) as e:
            raise HTTPException(status_code=400, detail=str(e))

        return _node_to_response(node)

    @router.post("/vectors", response_model=VectorResponse, status_code=201)
    def post_emit_vector(body: EmitVectorRequest) -> VectorResponse:
        """Emit a new financial vector."""
        try:
            cmd = EmitVectorCommand(
                source_node_id=EntityId(body.source_node_id),
                target_node_id=EntityId(body.target_node_id),
                amount=Decimal(body.amount),
                exchange_rate=Decimal(body.exchange_rate),
                lineage_token=body.lineage_token,
                transaction_id=(
                    EntityId(body.transaction_id) if body.transaction_id else None
                ),
                tags=dict(body.tags),
                effective_at=body.effective_at,
            )
            vector = emit_vector.execute(cmd)
        except InactiveNodeError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except (ValueError, DomainError) as e:
            raise HTTPException(status_code=400, detail=str(e))

        return _vector_to_response(vector)

    @router.get(
        "/nodes/{node_id}/balance",
        response_model=BalanceResponse,
        status_code=200,
    )
    def get_balance(node_id: UUID) -> BalanceResponse:
        """Evaluate a node's current balance."""
        try:
            query = BalanceQuery(node_id=EntityId(node_id))
            money = evaluate_balance.execute(query)
        except (ValueError, DomainError) as e:
            raise HTTPException(status_code=404, detail=str(e))

        return BalanceResponse(
            amount=str(money.amount),
            currency=money.currency,
        )

    return router


__all__ = ["create_ledger_router"]
