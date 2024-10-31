import asyncio
import logging
from asyncio import create_task

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

logger = logging.getLogger(__name__)

PING_INTERVAL = 25  # seconds
PING_PAYLOAD = b""


class WebSocketSession:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    @classmethod
    async def create(cls, websocket: WebSocket):
        instance = cls(websocket)
        await instance.accept()
        create_task(instance.ping())
        return instance

    async def accept(self):
        await self.websocket.accept()

    async def close(self):
        await self.websocket.close()

    async def receive_text(self):
        try:
            while True:
                text = await self.websocket.receive_text()
                yield text
        except WebSocketDisconnect:
            logging.info("WebSocket connection lost. Stopping receive_text task")
        except Exception as e:
            logging.error(f"Error in receive_text: {e}")
            raise

    async def send_text(self, text: str):
        try:
            logging.info(text)
            await self.websocket.send_text(text)
        except WebSocketDisconnect:
            logging.info("WebSocket connection lost. Stopping send_text task")
        except Exception as e:
            logging.error(f"Error in send_text: {e}")
            raise

    async def ping(self):
        try:
            while (
                self.websocket.application_state == WebSocketState.CONNECTED
                and self.websocket.client_state == WebSocketState.CONNECTED
            ):
                await self.websocket.send_bytes(PING_PAYLOAD)
                await asyncio.sleep(PING_INTERVAL)
        except RuntimeError as e:
            logging.error(f"Runtime error during ping: {e}")
            raise
