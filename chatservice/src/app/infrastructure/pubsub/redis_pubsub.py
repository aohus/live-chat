import asyncio
import logging

import redis.asyncio as redis
from app.interfaces.pubsub import PubSub
from redis.asyncio import ConnectionPool

logger = logging.getLogger(__name__)


class RedisPubSub(PubSub):
    def __init__(self):
        p_pool = ConnectionPool(host="redis", port=6379, max_connections=20)
        s_pool = ConnectionPool(host="redis", port=6379, max_connections=1000)

        self.publisher = redis.Redis(connection_pool=p_pool)
        self.subscriber = redis.Redis(connection_pool=s_pool)
        logging.info("Redis Client Connected Successfully")

    async def publish_message(self, channel_id: int, message: str):
        await self.publisher.publish(f"channel:{channel_id}", message)
        logging.info("publishing: channel=%s, message=%s", channel_id, message)

    async def subscribe_messages(self, channel_id: int):
        p = self.subscriber.pubsub()
        await p.subscribe(f"channel:{channel_id}")

        try:
            while True:
                message = await p.get_message(
                    ignore_subscribe_messages=True, timeout=None
                )
                if message:
                    logging.info(
                        "subscribe: channel=%s, message=%s", channel_id, message
                    )
                    yield message.get("data")  # bytes
                else:
                    await asyncio.sleep(0)  # be nice to th system
        finally:
            await p.unsubscribe(f"channel:{channel_id}")
            logging.info("unsubscribe: channel=%s", channel_id)
