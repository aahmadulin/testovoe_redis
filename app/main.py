from fastapi import FastAPI

from app.api.posts import router as posts_router
from app.utils.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app.utils.exception_handler import register_exception_handlers


setup_logging()

app = FastAPI(
    title="Blog API with Redis Cache",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

register_exception_handlers(app)
app.include_router(posts_router)

@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """
    Simple healthcheck endpoint for Docker health monitoring.

    Returns:
        dict[str, str]: Service health status.
    """
    # check if FastAPI process in alive
    return {"status": "ok"}