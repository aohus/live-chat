# app/monitoring.py

from opentelemetry import logs, metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.logs_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metrics_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing():
    resource = Resource(attributes={"service.name": "fastapi-chat-socket"})
    trace.set_tracer_provider(TracerProvider(resource=resource))

    # Configure OTLP Exporter for tracing
    span_exporter = OTLPSpanExporter(
        endpoint="http://otel-collector:4317", insecure=True
    )
    span_processor = BatchSpanProcessor(span_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)


def setup_metrics():
    resource = Resource(attributes={"service.name": "fastapi-chat-socket"})
    metrics.set_meter_provider(MeterProvider(resource=resource))

    # Configure OTLP Exporter for metrics
    metric_exporter = OTLPMetricExporter(
        endpoint="http://otel-collector:4317", insecure=True
    )
    metric_reader = PeriodicExportingMetricReader(
        exporter=metric_exporter, export_interval_millis=10000
    )
    metrics.get_meter_provider().add_metric_reader(metric_reader)


def setup_logging():
    resource = Resource(attributes={"service.name": "fastapi-chat-socket"})
    logs.set_logger_provider(LoggerProvider(resource=resource))

    # Configure OTLP Exporter for logs
    log_exporter = OTLPLogExporter(endpoint="http://otel-collector:4317", insecure=True)
    logs.get_logger_provider().add_log_exporter(log_exporter)


def setup_monitoring():
    setup_tracing()
    setup_metrics()
    setup_logging()
