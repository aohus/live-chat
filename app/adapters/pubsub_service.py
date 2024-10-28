import asyncio
from typing import Set, Dict

class PubSubService:
    def __init__(self):
        # 각 채널 ID별로 구독자 큐 세트를 관리
        self.channels: Dict[int, Set[asyncio.Queue]] = {}

    async def publish_message(self, channel_id: int, message: str):
        # 해당 채널의 모든 구독자 큐에 메시지를 전송
        if channel_id in self.channels:
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
                yield message
        finally:
            # 구독이 끝난 후 큐 제거
            self.channels[channel_id].remove(queue)
            if not self.channels[channel_id]:  # 해당 채널에 구독자가 없다면 채널 삭제
                del self.channels[channel_id]