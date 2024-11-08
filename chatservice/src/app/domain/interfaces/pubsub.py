import abc


class PubSub(abc.ABC):
    @abc.abstractmethod
    async def publish_message(self, channel_id: int, message: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def subscribe_messages(self, channel_id: int):
        raise NotImplementedError
