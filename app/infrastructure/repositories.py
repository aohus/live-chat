from typing import Optional
from app.domain.models import ChatRoom

class ChatRoomRepository:
    def __init__(self):
        self.rooms = {}  # 간단하게 메모리 내 저장소로 대체

    def get_chat_room(self, room_id: str) -> Optional[ChatRoom]:
        return self.rooms.get(room_id)

    def save_chat_room(self, room: ChatRoom):
        self.rooms[room.room_id] = room
