from fastapi import APIRouter

from api.schemas.query import MetricsResponse
from mcp.server import list_tools

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_model=MetricsResponse)
def metrics() -> MetricsResponse:
    return MetricsResponse(service="kg-assistant", version="0.1.0", available_tools=list_tools())
