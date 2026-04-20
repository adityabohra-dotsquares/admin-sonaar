from pydantic import BaseModel
from typing import List, Optional

class MenuItemSchema(BaseModel):
    title: str
    url: str
    order: int
    children: List['MenuItemSchema'] = []

    class Config:
        from_attributes = True

MenuItemSchema.model_rebuild()

class MenuSchema(BaseModel):
    name: str
    slug: str
    items: List[MenuItemSchema] = []

    class Config:
        from_attributes = True
