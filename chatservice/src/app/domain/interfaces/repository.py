import abc

from app.domain.entities.model import Message


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def save(self, message: Message) -> Message:
        # session.add(message)
        raise NotImplementedError
