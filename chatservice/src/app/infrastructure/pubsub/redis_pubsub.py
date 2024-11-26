import asyncio
import logging
import threading
from collections import defaultdict
from queue import Queue

import redis.asyncio as redis
from app.interfaces.pubsub import MessagePublisher, MessageSubscriber
from redis.asyncio import ConnectionPool

logger = logging.getLogger(__name__)


class RedisPublisher(MessagePublisher):
    def __init__(self):
        pool = ConnectionPool(host="redis", port=6379, max_connections=10)
        self.r = redis.Redis(connection_pool=pool)
        logging.info("Redis Publisher Connected Successfully")

    async def publish_message(self, channel_id: int, message: str):
        await self.r.publish(f"channel:{channel_id}", message)
        logging.info("publishing: channel=%s, message=%s", channel_id, message)


class RedisSubscriber(MessageSubscriber):
    def __init__(self):
        pool = ConnectionPool(host="redis", port=6379, max_connections=10)
        self.r = redis.Redis(connection_pool=pool)
        self.channels = dict()
        self.subscribers = defaultdict(list)
        logging.info("Redis Subscriber Connected Successfully")

    async def subscribe_messages(self, channel_id: int):
        if isinstance(channel_id, list):
            raise ValueError("channel_id must be an integer, not a list.")

        if channel_id not in self.channels:
            await self.subscribe_channel(channel_id)
        queue = asyncio.Queue()
        self.subscribers[channel_id].append(queue)
        try:
            logging.info("Start to subscribe messages from queue")
            while True:
                message = await queue.get()
                if message:
                    logging.info(message)
                    yield message
        finally:
            self.subscribers.get(channel_id).remove(queue)

    async def subscribe_channel(self, channel_id: int):
        logging.info(f"Subscribe channel:{channel_id} successfully")
        pubsub_obj = self.r.pubsub()
        await pubsub_obj.subscribe(f"channel:{channel_id}")

        message_queue = asyncio.Queue()
        self.channels[channel_id] = message_queue
        get_message_task = asyncio.create_task(
            self.get_message(pubsub_obj, message_queue)
        )
        broadcasting_task = asyncio.create_task(self.broadcasting(channel_id))
        asyncio.gather(get_message_task, broadcasting_task)

    async def get_message(
        self, pubsub_obj: redis.Redis.pubsub, message_queue: asyncio.Queue
    ):
        logging.info("Start to get messages from Redis")
        try:
            while True:
                message = await pubsub_obj.get_message(
                    ignore_subscribe_messages=True, timeout=None
                )
                if message:
                    await message_queue.put(message.get("data"))  # bytes
                else:
                    await asyncio.sleep(0)  # be nice to th system
        except Exception as e:
            raise e

    async def broadcasting(self, channel_id: int):
        logging.info(f"Start to broadcasting channel:{channel_id}")
        message_queue = self.channels[channel_id]
        subscribers = self.subscribers[channel_id]
        while True:
            message = await message_queue.get()
            message = message.decode("UTF-8")
            logging.info("subscribe: channel=%s, message=%s", channel_id, message)
            for queue in subscribers:
                await queue.put(message)
