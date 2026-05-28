import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from project_agent import __version__
from project_agent.api.routes import router
from project_agent.config import get_settings

logger = logging.getLogger("project_agent")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Project Knowledge Agent",
        description="과제별 지식 공간 + RAG 에이전트",
        version=__version__,
    )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        print(f"[VALIDATION ERROR] {request.method} {request.url}: {exc.errors()}")
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.middleware("http")
    async def log_upload_requests(request: Request, call_next):
        if "/upload" in request.url.path:
            ct = request.headers.get("content-type", "")
            cl = request.headers.get("content-length", "?")
            print(f"[DEBUG-UPLOAD] {request.method} {request.url} content-type={ct} content-length={cl}")
        response = await call_next(request)
        if "/upload" in request.url.path and response.status_code == 422:
            print(f"[DEBUG-UPLOAD] 422 RESPONSE for {request.method} {request.url}")
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "project_agent.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run()
