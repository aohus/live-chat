import asyncio
import json
import logging
from asyncio import create_task

from fastapi import WebSocket

from app.adapters.pubsub_service import PubSubService
from app.adapters.token_adapter import TokenAdapter
from app.domain.model import ContentFilter, Message

logger = logging.getLogger(__name__)


async def authenticate_token(token_adapters: TokenAdapter, tokens: str):
    for token in tokens:
        channel_id = await token_adapters.parse_token(token)
        if channel_id:
            return channel_id
    return None


class MessageRelayService:
    def __init__(self, pubsub_service: PubSubService):
        self.pubsub_service = pubsub_service

    async def start(self, websocket_session: WebSocket, channel_id: int):
        receive_task = create_task(
            self.receive_and_publish(websocket_session, channel_id)
        )
        send_task = create_task(self.subscribe_and_send(websocket_session, channel_id))

        await self.handle_tasks([receive_task, send_task])

    async def handle_tasks(self, tasks):
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        await self.process_completed_tasks(done)

        for task in pending:
            task.cancel()
        logging.info("WebSocket connection lost. Stopping the MessageRelayService.")

    async def process_completed_tasks(self, completed_tasks):
        for task in completed_tasks:
            if task.exception() is not None:
                logging.error(f"Task failed with exception: {task.exception()}")
            else:
                logging.info(
                    f"Task completed successfully with result: {task.result()}"
                )

    async def receive_and_publish(self, websocket_session: WebSocket, channel_id: int):
        async for text in websocket_session.receive_text():
            message = Message(**json.loads(text))
            if not self.has_forbidden_words(message):
                await self.pubsub_service.publish_message(
                    channel_id, json.dumps(message.to_dict())
                )

    async def subscribe_and_send(self, websocket_session: WebSocket, channel_id: int):
        async for sub_message in self.pubsub_service.subscribe_messages(channel_id):
            await websocket_session.send_text(sub_message.decode("utf-8"))

    def has_forbidden_words(self, message):
        # TODO: PrecessPool/Queue...
        content_filter = ContentFilter()
        return content_filter.has_forbidden_words(message.content)
