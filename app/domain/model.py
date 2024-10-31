from datetime import datetime


class Message:
    def __init__(self, type: str, content: str, user_id: str, timestamp: datetime):
        self.type = type
        self.content = content
        self.user_id = user_id
        self.timestamp = timestamp

    def filter(self):
        return True

    def to_dict(self):
        return {
            "type": self.type,
            "content": self.content,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
        }
