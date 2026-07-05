"""Entry point for the finance application."""

import uvicorn


def main() -> None:
    """Launch the FastAPI application."""
    uvicorn.run(
        "finance.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
