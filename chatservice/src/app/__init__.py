from api.v1 import router
from core.otel_monitoring import setup_monitoring
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware


def init_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_monitoring() -> None:
    setup_monitoring()


def init_middleware(app: FastAPI) -> None:
    """
    This library provides a ASGI middleware that can be used on any ASGI framework
    (such as Django, Starlette, FastAPI or Quart)
    to track requests timing through OpenTelemetry.
    """
    app.add_middleware(OpenTelemetryMiddleware)


def init_routers(app: FastAPI) -> None:
    app.include_router(router)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Live Chat",
        description="Live Chatting Server",
        version="1.0.0",
    )
    init_routers(app=app)
    init_monitoring()
    init_middleware(app=app)
    init_cors(app=app)
    return app


app = create_app()
