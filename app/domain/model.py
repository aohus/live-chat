from datetime import datetime

forbidden_words = {"shit"}


class Message:
    def __init__(self, type: str, content: str, user_id: str, timestamp: datetime):
        self.type = type
        self.content = content
        self.user_id = user_id
        self.timestamp = timestamp

    def has_forbidden_words(self):
        content = self.content.lower()

        for word in forbidden_words:
            if word in content:
                return True
        return False

    def to_dict(self):
        return {
            "type": self.type,
            "content": self.content,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
        }
