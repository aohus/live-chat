class PubSubService:
    async def send_message(self, channel_id: int, message: str):
        # 메시지를 pub/sub로 보내는 로직
        pass

    async def receive_messages(self, channel_id: int):
        # 메시지 수신 로직 (async generator로 구현)
        while True:
            yield f"Message for channel {channel_id}"
