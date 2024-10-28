from fastapi import WebSocket, APIRouter
from app.service.chat_service import ChatService
from app.adapters.token_service import TokenService
from app.adapters.pubsub_service import PubSubService
from fastapi.responses import HTMLResponse
import logging

logger = logging.getLogger("uvicorn")

chat_router = APIRouter()


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now();
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/api/v1/ws`);

            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var messageData = JSON.parse(event.data);

                var message = document.createElement('li');
                var content = document.createTextNode(`${messageData.sender.id}: ${messageData.content}`);
                message.appendChild(content);
                messages.appendChild(message);
            };

            function sendMessage(event) {
                var input = document.getElementById("messageText");
                
                // 메시지 데이터 구조를 작성
                var messageData = {
                    "type": "send_message",
                    "content": input.value,           // 입력된 메시지 내용
                    "sender": {
                        "id": client_id,              // 클라이언트 ID
                    },
                    "room_id": "room1",               // 메시지가 전송될 방의 ID
                    "timestamp": new Date().toISOString()  // 현재 시간 (ISO 8601 형식)
                };

                // JSON 문자열로 변환하여 전송
                ws.send(JSON.stringify(messageData));
                input.value = '';  // 입력 필드 초기화
                event.preventDefault();  // 기본 폼 제출 방지
            }
        </script>
    </body>
</html>
"""

@chat_router.get("/")
async def get():
    return HTMLResponse(html)


# 의존성 주입 설정
token_service = TokenService()
pubsub_service = PubSubService()
chat_service = ChatService(token_service, pubsub_service)

@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # token_headers = websocket.headers.get("X-WS-TOKEN", "").split(",")
    # channel_id = await chat_service.authenticate_token(token_headers)
    channel_id = 1

    if channel_id is None:
        await websocket.close()
        return

    # WebSocket 통신과 ping/pong 유지 관리
    await chat_service.handle_client_connection(websocket, channel_id)
