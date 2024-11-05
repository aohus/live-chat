# db에 저장하는 query
from app.domain.models import Message


class MessageRepository:
    async def save(self, message: Message) -> Message:
        # session.add(message)
        return message
