from fastapi import APIRouter, HTTPException, Depends
from site_settings.models import Menu, MenuItem
from fastapi_auth.schemas.menu import MenuSchema, MenuItemSchema
from typing import List
from asgiref.sync import sync_to_async

router = APIRouter()

@router.get("/{slug}", response_model=MenuSchema)
def get_menu(slug: str):
    try:
        print(slug)
        menu = Menu.objects.get(slug=slug)
        menu_items = MenuItem.objects.filter(menu=menu, parent=None, status=True).order_by('order')
        print(menu_items)
        def build_hierarchy(items):
            hierarchy = []
            for item in items:
                children = item.children.filter(status=True).order_by('order')
                item_schema = MenuItemSchema(
                    title=item.title,
                    url=item.url,
                    order=item.order,
                    children=build_hierarchy(children)
                )
                hierarchy.append(item_schema)
            return hierarchy

        hierarchy = build_hierarchy(menu_items)
        
        return MenuSchema(
            name=menu.name,
            slug=menu.slug,
            items=hierarchy
        )
    except Menu.DoesNotExist:
        raise HTTPException(status_code=404, detail="Menu not found")
