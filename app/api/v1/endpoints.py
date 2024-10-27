from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState
from app.application.chat_service import ChatService
from app.infrastructure.token_service import TokenService
from app.infrastructure.pubsub_service import PubSubService
from fastapi.responses import HTMLResponse
import logging

logger = logging.getLogger("uvicorn")

router = APIRouter()


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


# 의존성 주입 설정
token_service = TokenService()
pubsub_service = PubSubService()
chat_service = ChatService(token_service, pubsub_service)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    token_headers = websocket.headers.get("X-WS-TOKEN", "").split(",")
    channel_id = await chat_service.authenticate_token(token_headers)

    if channel_id is None:
        await websocket.close()
        return

    # WebSocket 통신과 ping/pong 유지 관리
    await chat_service.handle_client_connection(websocket, channel_id)
