import uvicorn
from fastapi import FastAPI

from project_agent import __version__
from project_agent.api.routes import router
from project_agent.config import get_settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Project Knowledge Agent",
        description="과제별 지식 공간 + RAG 에이전트",
        version=__version__,
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
