from fastapi import APIRouter

from api.schemas.query import QueryRequest, QueryResponse

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    return QueryResponse(answer=f"Placeholder answer for: {payload.question}", context=[])
