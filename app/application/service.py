# app/application/chat_service.py
from app.domain.models import ChatRoom, Message
from app.infrastructure.repositories import ChatRoomRepository
from typing import Dict

class ChatService:
    def __init__(self, room_repo: ChatRoomRepository):
        self.room_repo = room_repo
        self.active_connections: Dict[str, list] = {}  # room_id를 키로 하는 활성 연결 목록

    async def connect(self, websocket, room_id: str):
        """ 새로운 사용자가 연결될 때 호출 """
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket, room_id: str):
        """ 사용자가 연결을 끊을 때 호출 """
        self.active_connections[room_id].remove(websocket)

    async def broadcast(self, room_id: str, message: str):
        """ 방에 있는 모든 사용자에게 메시지 전송 """
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

    async def send_message(self, room_id: str, user_id: str, content: str):
        """ 메시지를 저장하고 브로드캐스트 준비 """
        room = self.room_repo.get_chat_room(room_id)
        if not room:
            raise ValueError("Chat room does not exist")
        
        message = Message(user_id=user_id, content=content)
        room.add_message(message)
        self.room_repo.save_chat_room(room)
        return message
