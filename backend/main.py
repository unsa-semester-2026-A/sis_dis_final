from fastapi import FastAPI

app = FastAPI(
    title="Spondylus Backend",
    description="Distributed banking system API",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
