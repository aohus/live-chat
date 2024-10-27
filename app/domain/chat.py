# 비즈니스 규칙과 도메인 로직을 정의
class ChatMessage:
    def __init__(self, content: str):
        self.content = content

    def transform(self):
        # 메시지 전처리 로직이 여기에 포함됩니다
        return self.content
