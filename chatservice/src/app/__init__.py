import logging
import os

from api.v1 import router
from core.otel_monitoring import setup_monitoring
from core.prometheus import PrometheusMiddleware, metrics, setting_otlp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

APP_NAME = os.environ.get("APP_NAME", "fastapi-chatservice")
OTLP_GRPC_ENDPOINT = os.environ.get("OTLP_GRPC_ENDPOINT", "otel-collector:4317")


def init_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_monitoring(app: FastAPI) -> None:
    app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
    # setup_monitoring()
    # Setting OpenTelemetry exporter
    setting_otlp(app, APP_NAME, OTLP_GRPC_ENDPOINT)


def init_log_filter() -> None:
    class EndpointFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return "GET /metrics" not in record.getMessage()

    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


def init_routers(app: FastAPI) -> None:
    app.include_router(router)
    # prometheus pull endpoints
    app.add_route("/metrics", metrics)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Live Chat",
        description="Live Chatting Server",
        version="1.0.0",
    )
    init_routers(app=app)
    init_monitoring(app=app)
    init_cors(app=app)
    init_log_filter()
    return app


app = create_app()
