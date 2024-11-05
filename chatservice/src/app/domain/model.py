import re
from datetime import datetime


class ContentFilter:
    FORBIDDEN_WORDS = ["shit", "scam", "spam"]

    def __init__(self):
        self.FORBIDDEN_PATTERN = self.compile_pattern()

    def compile_pattern(self):
        # 각 금지어를 `\W*`로 감싸도록 수정해 정규식 패턴 생성
        escaped_words = [re.escape(word) for word in self.FORBIDDEN_WORDS]
        pattern = (
            r"\b(" + "|".join([r"\W*".join(word) for word in escaped_words]) + r")\b"
        )
        return re.compile(pattern, re.IGNORECASE)

    def has_forbidden_words(self, text):
        return bool(self.FORBIDDEN_PATTERN.search(text))


class Message:
    def __init__(self, type: str, content: str, user_id: str, timestamp: datetime):
        self.type = type
        self.content = content
        self.user_id = user_id
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "type": self.type,
            "content": self.content,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
        }
