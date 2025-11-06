from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ItemCreateRequest(BaseModel):
    name: str


class ItemResponse(BaseModel):
    item_id: UUID
    user_id: UUID
    name: str
    is_bought: bool
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str