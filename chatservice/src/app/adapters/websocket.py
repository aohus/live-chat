import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketSession:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    @classmethod
    async def create(cls, websocket: WebSocket):
        instance = cls(websocket)
        await instance.accept()
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
            await self.close()
            logging.info("WebSocket connection lost. Stopping receive_text task")
        except Exception as e:
            await self.close()
            logging.error(f"Error in receive_text: {e}")
            raise

    async def send_text(self, text: str):
        try:
            logging.info(text)
            await self.websocket.send_text(text)
        except WebSocketDisconnect:
            await self.close()
            logging.info("WebSocket connection lost. Stopping send_text task")
        except Exception as e:
            await self.close()
            logging.error(f"Error in send_text: {e}")
            raise
