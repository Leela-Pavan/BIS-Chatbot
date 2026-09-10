from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.database import database_is_ready
from app.rag.postgres import DatabaseUnavailable
from app.rag.providers import create_embedding_provider
from app.rag.rag_service import answer_with_rag
from app.rag.schemas import AssistantResponse, QueryRequest

settings = get_settings()
embedding_provider = create_embedding_provider(
    settings.embedding_provider,
    settings.embedding_model,
    settings.embedding_dimensions,
)
app = FastAPI(
    title="BIS Sahayak API",
    version="0.1.0",
    description="Evidence-first API foundation for BIS Sahayak.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)


@app.middleware("http")
async def reject_oversized_requests(request: Request, call_next):
    content_length = request.headers.get("content-length")
    try:
        request_size = int(content_length) if content_length else 0
    except ValueError:
        return JSONResponse(
            status_code=400, content={"detail": "invalid content length"}
        )
    if request_size > settings.max_request_bytes:
        return JSONResponse(
            status_code=413,
            content={"detail": "request exceeds the configured size limit"},
        )
    return await call_next(request)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    return response


@app.get("/api/v1/health", tags=["system"])
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "bis-sahayak-api", "environment": settings.environment}


@app.get("/api/v1/ready", tags=["system"])
def ready() -> Dict[str, str]:
    if not database_is_ready(settings.database_url):
        raise HTTPException(status_code=503, detail="knowledge database is not ready")
    return {"status": "ready", "service": "bis-sahayak-api"}


@app.post(
    "/api/v1/assistant/query", response_model=AssistantResponse, tags=["assistant"]
)
def assistant_query(request: QueryRequest) -> AssistantResponse:
    try:
        return answer_with_rag(
            request,
            settings.database_url,
            embedding_provider=embedding_provider,
        )
    except DatabaseUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.post("/api/v1/standards/search", response_model=AssistantResponse, tags=["standards"])
def standards_search(request: QueryRequest) -> AssistantResponse:
    return assistant_query(request)
