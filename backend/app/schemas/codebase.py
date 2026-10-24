from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GithubIn(BaseModel):
    url: str


class CodebaseOut(BaseModel):
    id: int
    name: str
    source: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
