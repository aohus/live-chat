import asyncio
import json
import logging
from asyncio import create_task
from concurrent.futures import ProcessPoolExecutor

from app.entities.model import ContentFilter, Message
from app.interfaces.pubsub import PubSub
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class MessageRelayService:
    def __init__(self, pubsub: PubSub, max_workers: int = 2):
        self.pubsub = pubsub
        # 프로세스 풀을 생성하고 사용할 최대 프로세스 수를 설정
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.event_loop = asyncio.new_event_loop()

    async def start(self, websocket: WebSocket, channel_id: int):
        receive_task = create_task(self.receive_and_publish(websocket, channel_id))
        send_task = create_task(
            self.event_loop.run_in_executor(
                self.executor, self.subscribe_and_send, websocket, channel_id
            )
        )

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

    async def receive_and_publish(self, websocket: WebSocket, channel_id: int):
        while True:
            text = await websocket.receive_text()
            message = Message(**json.loads(text))
            if not self.has_forbidden_words(message):
                await self.pubsub.publish_message(
                    channel_id, json.dumps(message.to_dict())
                )

    async def subscribe_and_send(self, websocket: WebSocket, channel_id: int):
        async for sub_message in self.pubsub.subscribe_messages(channel_id):
            await websocket.send_text(sub_message.decode("utf-8"))

    def has_forbidden_words(self, message):
        # TODO: PrecessPool/Queue...
        content_filter = ContentFilter()
        return content_filter.has_forbidden_words(message.content)
