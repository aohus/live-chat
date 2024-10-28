import asyncio
import logging
from asyncio import create_task, sleep
from typing import Union

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from app.adapters.pubsub_service import PubSubService
from app.adapters.token_service import TokenService

PING_INTERVAL = 25  # seconds
PING_PAYLOAD = b""

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, token_service: TokenService, pubsub_service: PubSubService):
        self.token_service = token_service
        self.pubsub_service = pubsub_service

    async def authenticate_token(self, tokens):
        for token in tokens:
            channel_id = await self.token_service.parse_token(token)
            if channel_id:
                return channel_id
        return None

    async def handle_client_connection(self, websocket: WebSocket, channel_id: int):
        receive_task = create_task(self.receive_messages(websocket, channel_id))
        send_task = create_task(self.send_messages(websocket, channel_id))
        ping_task = create_task(self.ping(websocket))

        try:
            await asyncio.gather(receive_task, send_task, ping_task)
        except WebSocketDisconnect:
            logging.info("WebSocket disconnected")
            await self.cancel_tasks(receive_task, send_task, ping_task)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            await self.cancel_tasks(receive_task, send_task, ping_task)

    async def receive_messages(self, websocket: WebSocket, channel_id: int):
        try:
            while True:
                message = await websocket.receive_text()
                await self._publish_message(channel_id, message)
        except WebSocketDisconnect:
            logging.info("WebSocket disconnected - receive_task stopped")
            raise

    async def send_messages(self, websocket: WebSocket, channel_id: int):
        try:
            async for pub_message in self.pubsub_service.subscribe_messages(channel_id):
                processed_message = await self._process_message(pub_message)
                if processed_message:
                    await websocket.send_text(processed_message)
        except asyncio.CancelledError:
            logging.info("WebSocket disconnected - send_task stopped")

    async def ping(self, websocket: WebSocket):
        try:
            while websocket.application_state == WebSocketState.CONNECTED:
                await websocket.send_bytes(PING_PAYLOAD)
                await sleep(PING_INTERVAL)
        except RuntimeError:
            logging.error("Runtime error during ping")
            raise
        except asyncio.CancelledError:
            logging.info("WebSocket disconnected - ping_task stopped")

    async def cancel_tasks(self, *tasks):
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logging.info("All tasks have been cancelled and cleaned up.")

    async def _publish_message(self, channel_id: int, message: str):
        processed_message = await self._process_message(message)
        if processed_message:
            await self.pubsub_service.publish_message(channel_id, processed_message)

    async def _process_message(self, message: Union[bytes, str]) -> Union[str, dict]:
        if isinstance(message, bytes):
            return message.decode("utf-8")
        return message
