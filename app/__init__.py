from fastapi import FastAPI
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware

from api.v1 import router
from core.otel_monitoring import setup_monitoring


def init_monitoring() -> None:
    setup_monitoring()


def init_routers(app: FastAPI) -> None:
    app.include_router(router)


def init_middleware(app: FastAPI) -> None:
    app.add_middleware(OpenTelemetryMiddleware)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Live Chat",
        description="Live Chatting Server",
        version="1.0.0",
    )
    init_monitoring()
    init_routers(app=app)
    init_middleware(app=app)
    return app


app = create_app()
