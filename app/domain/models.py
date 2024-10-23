from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Message:
    user_id: str
    content: str
    timestamp: datetime = datetime.now()


@dataclass
class ChatRoom:
    room_id: str
    participants: List[str]  # user IDs
    messages: List[Message] = None

    def __post_init__(self):
        if self.messages is None:
            self.messages = []

    def add_message(self, message: Message):
        self.messages.append(message)
