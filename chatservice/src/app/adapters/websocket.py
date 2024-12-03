import logging
import socket
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketSession:
    """
    A wrapper class for managing WebSocket connections with enhanced error handling
    and resource management.
    """

    def __init__(self, websocket: WebSocket):
        self._websocket = websocket

    @classmethod
    @asynccontextmanager
    async def create(
        cls, websocket: WebSocket
    ) -> AsyncGenerator["WebSocketSession", None]:
        try:
            session = cls(websocket)
            await session.accept()
            await session._optimize_connection()
            yield session
        finally:
            await session.close()

    async def accept(self) -> None:
        await self._websocket.accept()

    async def _optimize_connection(self) -> None:
        try:
            socket_obj = self._websocket.transport.get_extra_info("socket")
            socket_obj.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except Exception as e:
            logger.warning(f"Could not optimize connection: {e}")

    async def close(self) -> None:
        try:
            await self._websocket.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")

    async def receive_text(self) -> AsyncGenerator[str, None]:
        try:
            while True:
                text = await self._websocket.receive_text()
                yield text
        except WebSocketDisconnect:
            logger.info("WebSocket connection closed by client")
        except Exception as e:
            logger.error(f"Error receiving message: {e}")

    async def send_text(self, text: str) -> None:
        try:
            logger.info(f"Sending message: {text}")
            await self._websocket.send_text(text)
        except WebSocketDisconnect:
            logger.info("WebSocket connection lost during send")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
