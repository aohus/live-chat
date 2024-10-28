from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Sender(BaseModel):
    id: int = Field(..., description="The unique identifier of the sender.")
    name: Optional[str] = Field(None, description="The name of the sender (optional).")


class Message(BaseModel):
    type: str = Field(..., description="Type of the message, e.g., 'send_message'.")
    content: str = Field(..., description="The actual content of the message.")
    sender: Sender = Field(..., description="Information about the sender.")
    room_id: str = Field(..., description="The ID of the chat room.")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Time when the message was sent."
    )
