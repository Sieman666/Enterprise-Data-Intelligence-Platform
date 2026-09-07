from fastapi import FastAPI

from app.api.analytics import router as analytics_router
from app.api.query import router as query_router
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="Enterprise Data Intelligence Platform API",
    version="0.1.0",
)

app.include_router(query_router)
app.include_router(analytics_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Enterprise Data Intelligence Platform API running"}
