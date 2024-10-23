from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.application.service import ChatService
from app.infrastructure.repositories import ChatRoomRepository

router = APIRouter()

# 의존성 주입: 리포지토리와 서비스를 연결
room_repo = ChatRoomRepository()
chat_service = ChatService(room_repo)


@router.websocket("/ws/room/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await chat_service.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()  # 클라이언트로부터 메시지 수신
            # 여기서 사용자 정보를 전달받는다고 가정
            user_id, content = data.split(": ", 1)
            await chat_service.send_message(room_id, user_id, content)
            await chat_service.broadcast(room_id, f"{user_id}: {content}")
    except WebSocketDisconnect:
        chat_service.disconnect(websocket, room_id)
