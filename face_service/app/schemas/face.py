from pydantic import BaseModel
from typing import List, Optional

class FaceRegistrationResponse(BaseModel):
    message: str

class FaceVerificationResponse(BaseModel):
    user_id: str
    verified: bool
    message: str

class FaceRecognitionResponse(BaseModel):
    identified: bool
    user_id: Optional[str]
    message: str

class UserListResponse(BaseModel):
    total: int
    users: List[str]

class MessageResponse(BaseModel):
    message: str
