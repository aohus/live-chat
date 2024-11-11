import time

from prometheus_client import Counter, Histogram
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# WebSocket Connections
WEBSOCKET_CONNECTIONS = Counter(
    "fastapi_websocket_connections", "Current WebSocket connections", ["app_name"]
)
MESSAGE_LATENCY = Histogram(
    "fastapi_message_latency_seconds", "Latency for message broadcasting", ["app_name"]
)


class PrometheusWebSocketMiddleware:
    def __init__(self, app: ASGIApp, app_name: str = "fastapi-app") -> None:
        self.app_name = app_name
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "websocket":
            await self.app(scope, receive, send)
            return

        async def receive_wrapper() -> Message:
            message = await receive()
            if message["type"] == "websocket.disconnect":
                WEBSOCKET_CONNECTIONS.labels(app_name=self.app_name).dec()
            return message

        # send: "websocket.accept", "websocket.close", "websocket.http.response.start", "websocket.send"
        async def send_wrapper(message: Message) -> None:
            message_type = message["type"]
            if message_type == "websocket.accept":
                WEBSOCKET_CONNECTIONS.labels(app_name=self.app_name).inc()
            await send(message)

        await self.app(scope, receive_wrapper, send_wrapper)
