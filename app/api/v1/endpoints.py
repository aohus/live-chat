from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.application.service import ChatService
from app.infrastructure.repositories import ChatRoomRepository
from fastapi.responses import HTMLResponse
import logging

logger = logging.getLogger("uvicorn")

router = APIRouter()

# 의존성 주입: 리포지토리와 서비스를 연결
room_repo = ChatRoomRepository()
chat_service = ChatService(room_repo)

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
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/api/v1/ws/room/1`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@router.get("/")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws/room/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await chat_service.connect(websocket, room_id)
    logger.info("Accept socket request")
    try:
        while True:
            data = await websocket.receive_text()  # 클라이언트로부터 메시지 수신
            # 여기서 사용자 정보를 전달받는다고 가정
            user_id, content = data.split(": ", 1)
            chat_service.send_message(room_id, user_id, content)
            # await chat_service.send_message(room_id, user_id, content)
            await chat_service.broadcast(room_id, f"{user_id}: {content}")
    except WebSocketDisconnect:
        chat_service.disconnect(websocket, room_id)
