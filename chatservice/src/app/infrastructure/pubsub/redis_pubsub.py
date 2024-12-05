import asyncio
import json
import logging
import multiprocessing
import pickle
import random
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import redis.asyncio as redis
from app.interfaces.pubsub import MessagePublisher, MessageSubscriber
from redis.asyncio import ConnectionPool

logger = logging.getLogger(__name__)


class RedisPublisher(MessagePublisher):
    def __init__(self):
        pool = ConnectionPool(host="redis", port=6379, max_connections=100)
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
        self.subscribers = multiprocessing.Manager().dict()
        self.batch_job_loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor()
        self.lock = threading.Lock()

        self.sampled_message_queue = multiprocessing.Queue()
        self._initialize_broadcasting()
        logging.info("Redis Subscriber Connected Successfully")

    def _initialize_broadcasting(self):
        def run_in_loop(subscribers, queue: multiprocessing.Queue):
            loop = asyncio.new_event_loop()
            loop.run_until_complete(
                self.broadcast_sampling_messages(subscribers, queue)
            )

        process = multiprocessing.Process(
            target=run_in_loop,
            args=(
                self.subscribers,
                self.sampled_message_queue,
            ),
        )
        process.start()

    async def subscribe_messages(self, websocket, channel_id: int):
        if channel_id not in self.channels:
            await self.subscribe_channel(channel_id)
        if channel_id not in self.subscribers:
            self.subscribers[channel_id] = []
        self.subscribers[channel_id].append(websocket)

    async def subscribe_channel(self, channel_id: int):
        logging.info(f"Subscribe channel:{channel_id} successfully")
        pubsub_obj = self.r.pubsub()
        await pubsub_obj.subscribe(f"channel:{channel_id}")

        messages = list()
        self.channels[channel_id] = messages
        get_message_task = asyncio.create_task(self.get_message(pubsub_obj, messages))
        sampling_message_task = self.batch_job_loop.run_in_executor(
            self.executor, self.sampling_message_in_batch, args=(channel_id, messages)
        )
        asyncio.gather(get_message_task, sampling_message_task)

    async def get_message(self, pubsub_obj: redis.Redis.pubsub, message_queue: list):
        logging.info("Start to get messages from Redis")
        try:
            while True:
                with self.lock:
                    message = await pubsub_obj.get_message(
                        ignore_subscribe_messages=True, timeout=None
                    )
                    if message:
                        message_queue.append(message.get("data"))  # bytes
                    else:
                        await asyncio.sleep(0)  # be nice to th system
        except Exception as e:
            raise e

    async def sampling_message_in_batch(self, channel_id: int, messages: list):
        while True:
            time.sleep(0.5)
            with self.lock:
                num_of_message = len(messages)
                sample_size = 2 if num_of_message > 20 else num_of_message * 0.1

                # 샘플링
                sampled_messages = random.sample(
                    messages, min(sample_size, num_of_message)
                )
                messages = list()
                await self.message_queue.put((channel_id, sampled_messages))

    async def broadcast_sampling_messages(self, message_queue: multiprocessing.Queue):
        while True:
            if message_queue:
                channel_id, messages = message_queue.get()
                subscribers = self.subscribers[channel_id]
                byte_message = pickle.dumps(messages)

                batch_size = 1000
                for i in range(0, len(subscribers), batch_size):
                    batch = [
                        ws.send_bytes(byte_message)
                        for ws in subscribers[i : i + batch_size]
                    ]
                    asyncio.gather(*batch)

                logging.info(
                    f"subscribe: channel={channel_id}, "
                    f"number-of-subscribers={len(subscribers)}, "
                    f"num-of-messages={len(messages)}"
                )
