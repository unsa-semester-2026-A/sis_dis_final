# Contributing to Wallet Service

To maintain code quality, type safety, and test coverage, every pull request (PR) merging into `develop` or `main` must satisfy all verification checks.

---

## Pre-merge Verification Checklist

Before pushing your branch or submitting a pull request, you must guarantee that:
1. All Python code is formatted correctly using **Ruff**.
2. There are no linting errors or warnings from **Ruff**.
3. Strict type checking passes with **Pyright**.
4. All unit and integration tests pass successfully with **Pytest**.

---

## Verification Commands

Run these commands inside the `app/backend/wallet-service` directory:

### 1. Formatter (Ruff)
Verify that all files comply with the formatting style guide:
```bash
uv run ruff format --check
```
To automatically format the code, run:
```bash
uv run ruff format
```

### 2. Linter (Ruff)
Run static analysis to detect code smell and check docstring standards:
```bash
uv run ruff check
```
To automatically fix safe lint issues, run:
```bash
uv run ruff check --fix
```

### 3. Type Checker (Pyright)
Run strict type checks to guarantee type safety across Hexagonal layers (Domain, Ports, Core, Adapters):
```bash
uv run pyright
```

### 4. Tests (Pytest)
Run the test suite to ensure no regressions:
```bash
uv run pytest -v
```
