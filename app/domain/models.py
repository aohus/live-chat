from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    user_id: str
    content: str
    timestamp: datetime = datetime.now()