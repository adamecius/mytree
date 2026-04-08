from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, description="Natural-language user question")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of context chunks")


class QueryResponse(BaseModel):
    answer: str
    context: list[str]


class BatchQueryRequest(BaseModel):
    questions: list[str] = Field(min_length=1, max_length=50)
    top_k: int = Field(default=5, ge=1, le=20)


class BatchQueryResponse(BaseModel):
    results: list[QueryResponse]


class MetricsResponse(BaseModel):
    service: str
    version: str
    available_tools: list[str]
