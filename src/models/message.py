from dataclasses import dataclass
from datetime import datetime


@dataclass
class MessageInfo:
    message_id: int
    chat_id: int
    partner_message_id: int
    timestamp: datetime
