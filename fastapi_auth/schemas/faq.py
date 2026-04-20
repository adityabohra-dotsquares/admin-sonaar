from pydantic import BaseModel

class FAQSchema(BaseModel):
    id: int
    type: str
    question: str
    answer: str
    order: int

    class Config:
        from_attributes = True
