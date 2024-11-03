import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from fastapi import WebSocketDisconnect

from app.domain.model import ContentFilter, Message
from app.service.message_relay import MessageRelayService


# Fake PubSubService for testing
class FakePubSubService:
    def __init__(self):
        self.published_messages = []

    async def publish_message(self, channel_id, message):
        self.published_messages.append((channel_id, message))

    async def subscribe_messages(self, channel_id):
        yield b"Test message from pubsub"


# Fake WebSocket for testing
class FakeWebSocket:
    def __init__(self, messages_to_receive):
        self.messages_to_receive = messages_to_receive
        self.sent_messages = []

    async def receive_text(self):
        start = datetime.now()
        try:
            while datetime.now() - start < timedelta(seconds=3):
                if self.messages_to_receive:
                    yield self.messages_to_receive.pop(0)
        except Exception as e:
            raise e

    async def send_text(self, message):
        self.sent_messages.append(message)


# Test fixtures for dependency injection
@pytest.fixture
def fake_pubsub_service():
    return FakePubSubService()


@pytest.fixture
def fake_websocket():
    return FakeWebSocket(
        [
            json.dumps(
                {
                    "type": "chat",
                    "content": "Hello",
                    "user_id": "user123",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        ]
    )


@pytest.fixture
def message_relay_service(fake_pubsub_service):
    return MessageRelayService(pubsub_service=fake_pubsub_service)


@pytest.mark.asyncio
async def test_start_tasks_scheduled(
    message_relay_service, fake_websocket, fake_pubsub_service
):
    # AsyncMock을 사용하여 run_until_first_complete 함수의 호출을 추적합니다.
    message_relay_service.run_until_first_complete = AsyncMock()

    # start() 호출
    await message_relay_service.start(fake_websocket, channel_id=1)

    # 현재 실행 중인 모든 비동기 작업 수집 / while 문은 3초 지나면 임의로 끝내도록 fake obj 생성함.
    all_tasks = asyncio.all_tasks()
    expected_tasks = {"receive_and_publish", "subscribe_and_send"}
    scheduled_tasks = {task._coro.__name__ for task in asyncio.all_tasks()}

    # run_until_first_complete가 실행된 횟수 확인
    message_relay_service.run_until_first_complete.assert_awaited_once()

    all_tasks = asyncio.all_tasks()
    print([task._coro.__name__ for task in all_tasks])

    assert expected_tasks.issubset(scheduled_tasks), (
        f"Expected tasks {expected_tasks} are not fully scheduled in the event loop. "
        f"Currently scheduled tasks: {scheduled_tasks}"
    )


@pytest.mark.asyncio
async def test_run_until_first_complete_cancel_tasks(
    message_relay_service, fake_websocket, fake_pubsub_service
):
    receive_task = asyncio.create_task(
        message_relay_service.receive_and_publish(fake_websocket, channel_id=1)
    )
    send_task = asyncio.create_task(
        message_relay_service.subscribe_and_send(fake_websocket, channel_id=1)
    )

    await message_relay_service.run_until_first_complete([receive_task, send_task])

    all_tasks = asyncio.all_tasks()

    # Check that both receive_and_publish and subscribe_and_send are not scheduled
    assert all(
        task._coro.__name__ not in ["receive_and_publish", "subscribe_and_send"]
        for task in all_tasks
    ), "Tasks receive_and_publish and/or subscribe_and_send were unexpectedly scheduled in the event loop"


# Test: receive_and_publish
@pytest.mark.asyncio
async def test_receive_and_publish(
    message_relay_service, fake_websocket, fake_pubsub_service
):
    await message_relay_service.receive_and_publish(fake_websocket, channel_id=1)

    # 메시지가 금지어 필터를 통과해 pubsub에 게시되었는지 확인
    assert len(fake_pubsub_service.published_messages) == 1
    print(fake_pubsub_service.published_messages[0])
    assert fake_pubsub_service.published_messages[0][1] == json.dumps(
        {
            "type": "chat",
            "content": "Hello",
            "user_id": "user123",
            "timestamp": fake_websocket.messages_to_receive[0]["timestamp"],
        }
    )


# # Test: subscribe_and_send
# @pytest.mark.asyncio
# async def test_subscribe_and_send(
#     message_relay_service, fake_websocket, fake_pubsub_service
# ):
#     await message_relay_service.subscribe_and_send(fake_websocket, channel_id=1)

#     # FakeWebSocket이 pubsub의 메시지를 올바르게 수신했는지 확인
#     assert fake_websocket.sent_messages == ["Test message from pubsub"]
