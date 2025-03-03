# backend/app/models/users.py
from pydantic import BaseModel, Field
from typing import List


class User(BaseModel):
    name: str = Field(..., min_length=1, max_length=30, pattern="^[a-zA-Z0-9_ ]+$")
    email: str = Field(
        ..., min_length=1, pattern="^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
    )
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=30, pattern="^[a-zA-Z0-9_ ]+$")
    groups: List[str] = []
