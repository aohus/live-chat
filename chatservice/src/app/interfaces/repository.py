import abc

from app.entities.model import Message


class Repository(abc.ABC):
    @abc.abstractmethod
    async def save(self, message: Message) -> Message:
        # session.add(message)
        raise NotImplementedError
