from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal, Union

class HistoryIn(BaseModel):
    userId: str
    sourceLang: str
    targetLang: str
    inputType: Literal["text", "voice", "image"]
    text: str
    result: str
    ts: Optional[datetime] = None

class HistoryOut(HistoryIn):
    id: str

class UserIn(BaseModel):
    email: EmailStr
    displayName: Optional[str] = None
    avatarUrl: Optional[str] = None
    role: Optional[str] = "student"
    createdAt: Optional[datetime] = None

class UserOut(UserIn):
    id: str

class ObjectIn(BaseModel):
    label: str
    confidence: Optional[float] = None
    imageUrl: Optional[str] = None
    langs: Optional[List[str]] = None
    ttsUrl: Optional[str] = None
    createdBy: Optional[str] = None
    ts: Optional[datetime] = None

class ObjectOut(ObjectIn):
    id: str

class FlagIn(BaseModel):
    key: str
    value: Union[str, bool, float, int, dict, list, None] = None
    type: Optional[Literal["bool", "str", "num", "json"]] = None
    scope: Optional[Literal["global", "user"]] = "global"
    updatedAt: Optional[datetime] = None

class FlagOut(FlagIn):
    id: str
