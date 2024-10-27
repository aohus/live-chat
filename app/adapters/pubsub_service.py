class PubSubService:
    async def send_message(self, channel_id: int, message: str):
        # 메시지를 pub/sub 시스템으로 전송하는 로직
        pass

    async def receive_messages(self, channel_id: int):
        # pub/sub 시스템으로부터 메시지를 비동기로 수신하는 로직
        while True:
            yield f"Message for channel {channel_id}"
