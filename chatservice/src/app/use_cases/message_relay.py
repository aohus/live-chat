import asyncio
import json
import logging
from asyncio import create_task

from app.entities.model import ContentFilter, Message
from app.interfaces.pubsub import PubSub
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class MessageRelayService:
    def __init__(self, pubsub: PubSub):
        self.pubsub = pubsub

    async def start(self, websocket_session: WebSocket, channel_id: int):
        receive_task = create_task(
            self.receive_and_publish(websocket_session, channel_id)
        )
        send_task = create_task(self.subscribe_and_send(websocket_session, channel_id))

        await self.run_until_first_complete([receive_task, send_task])

    async def run_until_first_complete(self, tasks: list):
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        await self.process_completed_tasks(done)

        for task in pending:
            task.cancel()
        logging.info("WebSocket connection lost. Stopping the MessageRelayService.")

    async def process_completed_tasks(self, completed_tasks: list):
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
                await self.pubsub.publish_message(
                    channel_id, json.dumps(message.to_dict())
                )

    async def subscribe_and_send(self, websocket_session: WebSocket, channel_id: int):
        async for sub_message in self.pubsub.subscribe_messages(channel_id):
            await websocket_session.send_text(sub_message.decode("utf-8"))

    def has_forbidden_words(self, message):
        # TODO: PrecessPool/Queue...
        content_filter = ContentFilter()
        return content_filter.has_forbidden_words(message.content)
