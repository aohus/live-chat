import logging
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
    async def create(cls, websocket: WebSocket):
        session = cls(websocket)
        await session.accept()
        return session

    async def accept(self) -> None:
        await self._websocket.accept()

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
