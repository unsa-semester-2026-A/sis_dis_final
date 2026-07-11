# Spondylus Backend — Distributed Personal Finance System

This directory contains the backend for the **Distributed Personal Finance System**, a university distributed systems final project. The system is designed using a **Pragmatic Domain-Driven Design (DDD)** approach combined with **Alistair Cockburn's Ports and Adapters (Hexagonal Architecture)**.

---

## 🏛️ Architecture & Philosophy

The project adheres to the **Dependency Rule**: dependency directions always point inwards towards the domain. Frameworks, drivers, and persistence mechanics are external details.

```mermaid
graph TD
    subgraph Primary Adapters (Driving)
        REST[FastAPI Routes]
    end

    subgraph Ports Layer
        InPorts[Inbound Ports / Protocols]
        OutPorts[Outbound Ports / Protocols]
    end

    subgraph Core Layer (Domain-Driven Design)
        UseCases[Use Cases / Business Logic]
        Domain[Entities / Value Objects]
    end

    subgraph Secondary Adapters (Driven)
        JSONStore[JSON File Store]
    end

    REST --> InPorts
    InPorts --> UseCases
    UseCases --> Domain
    UseCases --> OutPorts
    JSONStore -.-> OutPorts
```

### 1. The Core Layer (Domain & Use Cases)
- **Entities & Value Objects:** Houses business invariants and logic. In Spondylus, these are represented as immutable structures (`frozen` dataclasses):
  - **`Money` (Value Object):** Enforces currency homogeneity during calculations.
  - **`Node` (Entity):** Classifies vertices as `ASSET`, `LIABILITY`, `SOURCE`, or `SINK`.
  - **`Vector` (Entity):** Append-only mutation edges moving value from a source node to a target node.
- **Use Cases:** Coordinate flow execution. Independent of databases, frameworks, or interfaces.

### 2. The Ports Layer (Hexagonal Boundaries)
- **Inbound (Driving) Ports:** Define what operations the application core makes available to the outer world (e.g. `CreateNodePort`, `EmitVectorPort`, `EvaluateBalancePort`). Typed strictly using `typing.Protocol`.
- **Outbound (Driven) Ports:** Define what operations the application core needs from the external world (e.g., `NodeRepository`, `VectorRepository`). Wires the business engine to storage adapters.

### 3. The Adapters Layer (Infrastructure)
- **Primary (Driving) Adapters:** Trigger core execution. In Spondylus, this is the [FastAPI REST routes](file:///home/alvaro9rqc/1_Pacha/1-unsa/7_S/dis/final/backend/src/finance/ledger/adapters/rest/).
- **Secondary (Driven) Adapters:** Implement outbound ports. To satisfy Distributed File System (DFS) constraints without a database server, we partition ledger entities into [node-specific JSON files](file:///home/alvaro9rqc/1_Pacha/1-unsa/7_S/dis/final/backend/src/finance/ledger/adapters/file_store/repositories.py).

---

## 🧪 Co-located Testing

To avoid codebase structure fragmentation and maintain a high level of code locality, **all tests are placed in the same directory as the source code they test**, rather than in a separate `tests/` directory:

- Test files must follow the prefix pattern `test_*.py`.
- Examples:
  - Domain tests: `src/finance/ledger/domain/test_ledger_domain.py` -> tests `node.py` and `vector.py`.
  - Use case tests: `src/finance/ledger/core/test_use_cases.py` -> tests `create_node.py`, `emit_vector.py`, etc.
  - Adapter tests: `src/finance/ledger/adapters/rest/test_rest_adapter.py` -> tests the FastAPI router.

This layout ensures that when navigating packages, developer context and assertions remain coupled to the relevant domain models or adapters.

---

## ✍️ Coding Standards & Docstrings

We strictly adhere to the **Google Python Style Guide** for code docstrings. Every module, class, and function must be fully documented:

```python
def execute(self, query: BalanceQuery) -> Money:
    """Calculate the balance of a financial node.

    Formulates: Inflows - Outflows.

    Args:
        query: The criteria identifying the target node and period bounds.

    Returns:
        The calculated balance wrapped in a Money value object.

    Raises:
        DomainError: If the target node is missing or deactivated.
    """
```

### Static Type Checks & Formatting
- **Linter/Formatter:** [Ruff](https://github.com/astral-sh/ruff) is used for extreme speed, formatting code blocks, and sorting imports (`ruff check` & `ruff format`).
- **Strict Typing:** Managed via [Pyright](https://github.com/microsoft/pyright) set to `"strict"` checking mode. Every variable, parameter, and return value must have explicit types (avoiding `Any`/`Unknown`).

---

## 🚀 Environment Setup

We utilize `uv` as the modern, high-speed Python package manager.

### Prerequisites
Install `uv` (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installing Dependencies & Running Virtual Env
Generate the `.venv` and sync dependencies:
```bash
uv sync
```

### Running Checks & Tests
```bash
# Run pytest test suite
uv run pytest

# Check code styling & formatting
uv run ruff check src/
uv run ruff format src/ --check

# Verify strict type safety
uv run pyright src/
```

### Running the API locally
```bash
uv run fastapi dev src/finance/app.py
```
