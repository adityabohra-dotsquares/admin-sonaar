from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class SocialMediaLinkRead(BaseModel):
    id: int
    platform: str
    url: str
    icon_class: str
    order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # If needed for compatibility with older pydantic
        # orm_mode = True 
