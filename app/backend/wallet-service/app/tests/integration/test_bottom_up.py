"""Bottom-up integration tests.

Tests the system from the lowest level adapters (file system JSON repositories)
upwards, coupling them with the business use cases to verify direct database/file
integration with core logic without any mock or HTTP layer.
"""

from decimal import Decimal
from pathlib import Path

from app.ledger.adapters.file_store import FileNodeRepository, FileVectorRepository
from app.ledger.core.create_node import CreateNodeUseCase
from app.ledger.core.emit_vector import EmitVectorUseCase
from app.ledger.core.evaluate_balance import EvaluateBalanceUseCase
from app.ledger.core.node_type import NodeType
from app.ledger.ports.inbound import BalanceQuery, CreateNodeCommand, EmitVectorCommand
from app.ledger.ports.outbound import NodeRepository, VectorRepository
from app.shared import Money, new_id


def test_bottom_up_persistence_to_usecase_integration(tmp_path: Path) -> None:
    """Verify bottom-up integration between storage files and use cases."""
    # 1. Instantiate the lowest layer adapters (real filesystem on tmp_path)
    node_repo: NodeRepository = FileNodeRepository(data_dir=tmp_path)
    vector_repo: VectorRepository = FileVectorRepository(data_dir=tmp_path)

    # 2. Instantiate core use case handlers injecting the real adapters
    create_node_uc = CreateNodeUseCase(node_repo=node_repo)
    emit_vector_uc = EmitVectorUseCase(node_repo=node_repo, vector_repo=vector_repo)
    evaluate_balance_uc = EvaluateBalanceUseCase(
        node_repo=node_repo, vector_repo=vector_repo
    )

    user_id = new_id()

    # 3. Create nodes using CreateNodeUseCase -> writes directly to disk
    bank = create_node_uc.execute(
        CreateNodeCommand(
            user_id=user_id,
            name="Savings Account",
            node_type=NodeType.ASSET,
            currency="USD",
        )
    )
    expense = create_node_uc.execute(
        CreateNodeCommand(
            user_id=user_id,
            name="Electricity Bill",
            node_type=NodeType.SINK,
            currency="USD",
        )
    )

    # Verify files exist in directory (Bottom-up validation of lower layer)
    assert (tmp_path / "nodes" / f"{bank.id}.json").exists()
    assert (tmp_path / "nodes" / f"{expense.id}.json").exists()

    # 4. Emit vector using EmitVectorUseCase -> appends directly to disk
    vector = emit_vector_uc.execute(
        EmitVectorCommand(
            source_node_id=bank.id,
            target_node_id=expense.id,
            amount=Decimal("150.75"),
        )
    )
    assert (tmp_path / "vectors" / f"{vector.id}.json").exists()

    # 5. Evaluate balance using EvaluateBalanceUseCase -> queries and compiles from disk
    balance = evaluate_balance_uc.execute(BalanceQuery(node_id=bank.id))
    assert balance == Money(Decimal("-150.75"), "USD")
