import asyncio
from asyncio import create_task, sleep
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from pydantic import ValidationError

from app.adapters.pubsub_service import PubSubService
from app.adapters.token_service import TokenService
from app.schema.message import Message

PING_INTERVAL = 25  # seconds
PING_PAYLOAD = b""


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
                pass

        async def send_messages():
            try:
                async for pub_message in self.pubsub_service.subscribe_messages(
                    channel_id
                ):
                    processed_message = await self._process_message(pub_message)
                    if processed_message:
                        await websocket.send_text(processed_message.json())
            except WebSocketDisconnect:
                pass

        # async def ping():
        #     try:
        #         while websocket.application_state == WebSocketState.CONNECTED:
        #             await websocket.send_bytes(PING_PAYLOAD)
        #             await sleep(PING_INTERVAL)
        #     except WebSocketDisconnect:
        #         pass

        receive_task = create_task(receive_messages())
        send_task = create_task(send_messages())
        # ping_task = create_task(ping())
        await asyncio.gather(receive_task, send_task)

    async def _publish_message(self, channel_id: int, message: str):
        processed_message = await self._process_message(message)
        if processed_message:
            await self.pubsub_service.publish_message(
                channel_id, processed_message.json()
            )

    async def _process_message(self, message: str) -> Optional[Message]:
        try:
            processed_message = Message.parse_raw(message)
            return processed_message
        except ValidationError as e:
            print(f"Error parsing message: {e}")
            return None
