import logging

from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.adapters.pubsub_service import PubSubService
from app.adapters.token_adapter import TokenAdapter
from app.adapters.websocket import WebSocketSession
from app.service.message_relay import MessageRelayService, authenticate_token

logger = logging.getLogger(__name__)

chat_router = APIRouter()


templates = Jinja2Templates(directory="templates")


@chat_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


# 의존성 주입 설정
token_adapter = TokenAdapter()
pubsub_service = PubSubService()
message_relay_service = MessageRelayService(pubsub_service)


@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    websocket_session = await WebSocketSession.create(websocket)

    # token_headers = websocket.headers.get("X-WS-TOKEN", "").split(",")
    # channel_id = await authenticate_token(token_adapter, token_headers)
    channel_id = 1

    if channel_id is None:
        await websocket_session.close()
        return

    # WebSocket 통신과 ping/pong 유지 관리
    await message_relay_service.start(websocket_session, channel_id)
