from datetime import datetime

from app.domain.model import Message

timestamp = datetime.now()


def test_message_model_init():
    message = Message(
        type="send_message",
        content="test message, nice word",
        user_id="1234",
        timestamp=timestamp,
    )
    assert message.type == "send_message"
    assert message.content == "test message, nice word"
    assert message.user_id == "1234"
    assert message.timestamp == timestamp


def test_message_model_not_has_forbidden_words():
    message = Message(
        type="send_message",
        content="test message, nice word",
        user_id="1234",
        timestamp=timestamp,
    )
    result = message.has_forbidden_words()
    assert result is False


def test_message_model_has_forbidden_words():
    message = Message(
        type="send_message",
        content="test message, bad word, shit",
        user_id="1234",
        timestamp=timestamp,
    )
    result = message.has_forbidden_words()
    assert result is True


# def test_message_model_content_longer_than_500():
#     message = Message(
#         type="send_message",
#         content="test message",
#         user_id="1234",
#         timestamp=timestamp,
#     )
#     result = message.filter()
#     assert result is False


def test_messsage_model_to_dict():
    message_dict = {
        "type": "send_message",
        "content": "test message",
        "user_id": "1234",
        "timestamp": timestamp,
    }
    message = Message(
        type="send_message",
        content="test message",
        user_id="1234",
        timestamp=timestamp,
    )
    assert message.to_dict() == message_dict
