from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    type: str
    username: str
    content: str
    timestamp: str
    users: Optional[List[str]] = None
