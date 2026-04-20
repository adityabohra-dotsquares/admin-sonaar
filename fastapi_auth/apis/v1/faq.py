from fastapi import APIRouter
from cms.models import FAQ
from fastapi_auth.schemas.faq import FAQSchema
from typing import List, Optional

router = APIRouter()

@router.get("", response_model=List[FAQSchema])
def get_faqs():
    query = FAQ.objects.filter(is_published=True)
    # if type:
    #     query = query.filter(type=type)
    
    return list(query)
