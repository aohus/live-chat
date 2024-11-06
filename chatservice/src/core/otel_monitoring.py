# app/monitoring.py
import logging
import os

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer_provider, set_tracer_provider

OTEL_EXPORTER_OTLP_ENDPOINT = os.environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
)


def setup_metrics():
    resource = Resource(attributes={"service.name": "fastapi-chat-socket"})
    # Configure OTLP Exporter for metrics
    metric_exporter = OTLPMetricExporter(
        endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,
    )
    metric_reader = PeriodicExportingMetricReader(
        exporter=metric_exporter, export_interval_millis=10000
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    set_meter_provider(meter_provider)


def setup_tracing():
    resource = Resource(attributes={"service.name": "fastapi-chat-socket"})
    set_tracer_provider(TracerProvider(resource=resource))

    # Configure OTLP Exporter for tracing
    span_exporter = OTLPSpanExporter(
        endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,
    )
    span_processor = BatchSpanProcessor(span_exporter)
    get_tracer_provider().add_span_processor(span_processor)


def setup_logging():
    """
    # Create different namespaced loggers
    # It is recommended to not use the root logger with OTLP handler
    # so telemetry is collected only for the application
    """
    resource = Resource(attributes={"service.name": "fastapi-chat-socket"})
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    log_exporter = OTLPLogExporter(
        endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

    # Attach OTLP handler to root logger
    logging.getLogger().addHandler(handler)
    logger1 = logging.getLogger("myapp.area1")
    logger2 = logging.getLogger("myapp.area2")

    logger1.debug("Logger Test.")
    logger1.info("Logger Test.")
    logger2.warning("Logger Test.")
    logger2.error("Logger Test.")


def setup_monitoring():
    setup_metrics()
    setup_tracing()
    setup_logging()
