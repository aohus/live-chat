import asyncio
from asyncio import create_task, sleep

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

app = FastAPI()

PING_INTERVAL = 25  # 25 seconds
PING_PAYLOAD = b""


# 의존성 주입과 서비스는 DI나 기타 패턴에 맞춰 처리할 수 있음
class TokenService:
    async def parse_token(self, token: str) -> int:
        # 토큰을 파싱하여 채널 ID를 반환하는 로직
        pass


class PubSubService:
    async def send_message(self, channel_id: int, message: str):
        # 메시지를 pub/sub로 보내는 로직
        pass

    async def receive_messages(self, channel_id: int):
        # 메시지 수신 로직 (async generator로 구현)
        while True:
            yield f"Message for channel {channel_id}"


class ChattingService:
    async def process_message(self, message: str):
        # 메시지를 처리하는 로직
        return message


token_service = TokenService()
pubsub_service = PubSubService()
chatting_service = ChattingService()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # 클라이언트가 보낸 헤더에서 토큰 추출
    token_headers = websocket.headers.get("X-WS-TOKEN", "").split(",")

    # 채널 ID 추출
    channel_id = None
    for token in token_headers:
        channel_id = await token_service.parse_token(token)
        if channel_id:
            break

    if channel_id is None:
        await websocket.close()
        return

    async def receive_messages():
        try:
            while True:
                message = await websocket.receive_text()
                processed_message = await chatting_service.process_message(message)
                await pubsub_service.send_message(channel_id, processed_message)
        except WebSocketDisconnect:
            pass

    async def send_messages():
        try:
            async for pub_message in pubsub_service.receive_messages(channel_id):
                await websocket.send_text(pub_message)
        except WebSocketDisconnect:
            pass

    async def ping():
        try:
            while True:
                if websocket.application_state == WebSocketState.CONNECTED:
                    await websocket.send_bytes(PING_PAYLOAD)
                await sleep(PING_INTERVAL)
        except WebSocketDisconnect:
            pass

    # 각각의 task 비동기로 실행
    receive_task = create_task(receive_messages())
    send_task = create_task(send_messages())
    ping_task = create_task(ping())

    await asyncio.gather(receive_task, send_task, ping_task)
