import abc
import asyncio
import json
import logging
from dataclasses import asdict
from typing import Dict, Set

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class AbstractPubSubService(abc.ABC):
    @abc.abstractmethod
    async def publish_message(self, channel_id: int, message: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def subscribe_messages(self, channel_id: int):
        raise NotImplementedError


class InMemoryPubSubService(AbstractPubSubService):
    def __init__(self):
        # 각 채널 ID별로 구독자 큐 세트를 관리
        # 단일 프로세스에서만 동작함
        self.channels: Dict[int, Set[asyncio.Queue]] = {}

    async def publish_message(self, channel_id: int, message: str):
        # 해당 채널의 모든 구독자 큐에 메시지를 전송
        if channel_id in self.channels:
            logging.info("publishing: channel=%s, message=%s", channel_id, message)
            for queue in self.channels[channel_id]:
                await queue.put(message)

    async def subscribe_messages(self, channel_id: int):
        # 새로운 구독자용 큐 생성 및 채널에 추가
        queue = asyncio.Queue()
        if channel_id not in self.channels:
            self.channels[channel_id] = set()
        self.channels[channel_id].add(queue)

        try:
            while True:
                # 구독자가 큐에서 메시지를 받아 yield
                message = await queue.get()
                logging.info("subscribe: channel=%s, message=%s", channel_id, message)
                yield message
        finally:
            # 구독이 끝난 후 큐 제거
            self.channels[channel_id].remove(queue)
            if not self.channels[channel_id]:  # 해당 채널에 구독자가 없다면 채널 삭제
                del self.channels[channel_id]


class PubSubService(AbstractPubSubService):
    def __init__(self):
        self.r = redis.Redis(host="localhost", port=6379)
        logging.info("redis connected")

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
        finally:
            await p.unsubscribe(f"channel:{channel_id}")
            logging.info("unsubscribe: chanel=%s", channel_id)
