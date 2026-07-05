"""Entry point for the wallet-service FastAPI application.

This module initializes the FastAPI application, wires dependencies,
and registers API routers.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    """Read the root endpoint.

    Returns:
        dict: A greeting message.
    """
    return {"message": "Hello World from FastAPI, uv, and Uvicorn!"}
