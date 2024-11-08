import logging

from api.v1 import router
from core.config import config
from core.otel_monitoring import setup_monitoring
from core.utils import PrometheusMiddleware, metrics, setting_otlp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def init_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_monitoring(app: FastAPI) -> None:
    app.add_middleware(PrometheusMiddleware, app_name=config.APP_NAME)
    # setup_monitoring()
    # Setting OpenTelemetry exporter
    # setting_otlp(app, config.APP_NAME, config.OTEL_EXPORTER_OTLP_ENDPOINT)


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
    # init_monitoring(app=app)
    init_log_filter()
    init_cors(app=app)
    return app


app = create_app()
