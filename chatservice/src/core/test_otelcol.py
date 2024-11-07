import logging
import time

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Collector endpoint 설정
OTEL_EXPORTER_OTLP_ENDPOINT = (
    "http://otel-collector:4317"  # Docker Compose 환경에 맞춰 설정
)

# Tracer provider 설정
resource = Resource(attributes={"service.name": "test-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# OTLP Exporter 및 Span Processor 설정
otlp_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

LoggingInstrumentor().instrument(set_logging_format=True)
logger1 = logging.getLogger("myapp.area1")
logger1.debug("Logger Test.")

# 샘플 트레이스 전송
with tracer.start_as_current_span("root_span") as root_span:
    time.sleep(0.1)  # 간단한 작업 대기
    with tracer.start_as_current_span("child_span") as child_span:
        time.sleep(0.2)  # 다른 작업 대기

print("Trace sent to OpenTelemetry Collector!")
