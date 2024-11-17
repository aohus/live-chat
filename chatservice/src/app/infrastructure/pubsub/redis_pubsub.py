import asyncio
import logging

import redis.asyncio as redis
from app.interfaces.pubsub import PubSub

logger = logging.getLogger(__name__)


class RedisPubSub(PubSub):
    def __init__(self):
        self.r = redis.Redis(host="redis", port=6379)
        logging.info("Redis Client Connected Successfully")

    async def publish_message(self, channel_id: int, message: str):
        await self.r.publish(f"channel:{channel_id}", message)
        logging.info("publishing: channel=%s, message=%s", channel_id, message)

    async def subscribe_messages(self, channel_id: int):
        p = self.r.pubsub()
        await p.subscribe(f"channel:{channel_id}")

        try:
            while True:
                message = await p.get_message(ignore_subscribe_messages=True)
                if message:
                    logging.info(
                        "subscribe: channel=%s, message=%s", channel_id, message
                    )
                    yield message.get("data")  # bytes
                else:
                    await asyncio.sleep(0.001)  # be nice to th system
        finally:
            await p.unsubscribe(f"channel:{channel_id}")
            logging.info("unsubscribe: channel=%s", channel_id)
