from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal


class ItemCreateRequest(BaseModel):
    name: str
    list_type: Literal["to_buy", "items"]


class ItemMoveRequest(BaseModel):
    to_list: Literal["to_buy", "items"]


class ItemResponse(BaseModel):
    item_id: UUID
    user_id: UUID
    name: str
    is_bought: bool
    list_type: str
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str