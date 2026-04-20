from fastapi import APIRouter, Depends
from typing import List
from adminuser.models.social_media import SocialMediaLink
from fastapi_auth.schemas.social_media import SocialMediaLinkRead

router = APIRouter()

@router.get("/links", response_model=List[SocialMediaLinkRead])
def list_social_media_links():
    """
    Returns a list of all active social media links, ordered by priority.
    """
    links = SocialMediaLink.objects.filter(is_active=True).order_by("order", "platform")
    return list(links)
