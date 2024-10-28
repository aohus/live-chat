import asyncio
import json
import logging
from asyncio import create_task, sleep
from typing import Union

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from app.adapters.pubsub_service import PubSubService
from app.adapters.token_service import TokenService
from app.schema.message import Message

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
        async def receive_messages():
            try:
                while True:
                    message = await websocket.receive_text()
                    await self._publish_message(channel_id, message)
            except WebSocketDisconnect:
                logging.info("websocket disconnected - recieve_task stopped")
                raise

        async def send_messages():
            try:
                async for pub_message in self.pubsub_service.subscribe_messages(
                    channel_id
                ):
                    processed_message = await self._process_message(pub_message)
                    if processed_message:
                        await websocket.send_text(processed_message)
            except asyncio.CancelledError:
                logging.info("websocket disconnected - send_task stopped")

        async def ping():
            try:
                while (
                    websocket.application_state == WebSocketState.CONNECTED
                    and websocket.client_state == WebSocketState.CONNECTED
                ):
                    await websocket.send_bytes(PING_PAYLOAD)
                    await sleep(PING_INTERVAL)
            except RuntimeError:
                raise
            except asyncio.CancelledError:
                logging.info("websocket disconnected - ping_task stopped")

        async def cancel_tasks(*tasks):
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            logging.info("All tasks have been cancelled and cleaned up.")

        receive_task = create_task(receive_messages())
        send_task = create_task(send_messages())
        ping_task = create_task(ping())

        try:
            await asyncio.gather(receive_task, send_task, ping_task)
        except WebSocketDisconnect:
            logging.info("WebSocket disconnected")
            await cancel_tasks(receive_task, send_task, ping_task)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            await cancel_tasks(receive_task, send_task, ping_task)

    async def _publish_message(self, channel_id: int, message: str):
        processed_message = await self._process_message(message)
        if processed_message:
            await self.pubsub_service.publish_message(channel_id, processed_message)

    async def _process_message(self, message: Union[bytes, str]) -> Union[str, dict]:
        if isinstance(message, bytes):
            processed_message = message.decode("utf-8")
        elif isinstance(message, str):
            processed_message = message
        return processed_message
        # try:
        #     processed_message = Message.model_validate_json(message)
        #     return processed_message
        # except ValidationError as e:
        #     logging.error(f"Error parsing message: {e}")
        #     return None
