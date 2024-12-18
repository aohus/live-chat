import logging

from app.adapters.websocket import WebSocketSession
from app.infrastructure.pubsub.redis_pubsub import RedisPublisher, RedisSubscriber
from app.use_cases.message_relay import MessageRelayService
from app.use_cases.token_validator import TokenValidator
from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)

chat_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@chat_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


# 의존성 주입 설정
token_validator = TokenValidator()
redis_publisher = RedisPublisher()
redis_subscriber = RedisSubscriber()
message_relay_service = MessageRelayService(redis_publisher, redis_subscriber)


@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    wss = await WebSocketSession.create(websocket)
    # token_headers = wss.headers.get("X-WS-TOKEN", "").split(",")
    # logging.info("token header", token_headers)
    # channel_id = await token_validator.authenticate_token(token_headers)

    channel_id = 1

    if channel_id is None:
        await wss.close()
        return

    # WebSocket 통신과 ping/pong 유지 관리
    await message_relay_service.start(wss, channel_id)
