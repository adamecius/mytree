from fastapi import APIRouter

from api.schemas.query import BatchQueryRequest, BatchQueryResponse, QueryRequest, QueryResponse
from mcp.tools.retrieve_tool import retrieve

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    context = retrieve(payload.question, k=payload.top_k)
    return QueryResponse(answer=f"Placeholder answer for: {payload.question}", context=context)


@router.post("/batch_query", response_model=BatchQueryResponse)
def batch_query(payload: BatchQueryRequest) -> BatchQueryResponse:
    results = [
        QueryResponse(
            answer=f"Placeholder answer for: {question}",
            context=retrieve(question, k=payload.top_k),
        )
        for question in payload.questions
    ]
    return BatchQueryResponse(results=results)
