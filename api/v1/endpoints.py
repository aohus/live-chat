from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.adapters.pubsub_service import PubSubService
from app.adapters.token_service import TokenService
from app.service.chat_service import ChatService

chat_router = APIRouter()


templates = Jinja2Templates(directory="templates")


@chat_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


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
