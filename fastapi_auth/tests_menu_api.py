from django.test import TransactionTestCase, Client
from site_settings.models import Menu, MenuItem
from fastapi.testclient import TestClient
from fastapi_auth.main import fastapi_app

class MenuAPITest(TransactionTestCase):
    reset_sequences = True
    def setUp(self):
        self.menu = Menu.objects.create(name="Main Menu", slug="main-menu")
        self.item1 = MenuItem.objects.create(menu=self.menu, title="Home", url="/", order=1)
        self.item2 = MenuItem.objects.create(menu=self.menu, title="Products", url="/products", order=2)
        MenuItem.objects.create(menu=self.menu, parent=self.item2, title="Sub-product", url="/products/sub", order=1)
        
        self.client = TestClient(fastapi_app)

    def test_get_menu_endpoint(self):
        response = self.client.get("/api/v1/menu/main-menu")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], "Main Menu")
        self.assertEqual(data['slug'], "main-menu")
        self.assertEqual(len(data['items']), 2)
        
        # Check hierarchy
        products_item = next(item for item in data['items'] if item['title'] == 'Products')
        self.assertEqual(len(products_item['children']), 1)
        self.assertEqual(products_item['children'][0]['title'], 'Sub-product')

    def test_get_menu_not_found(self):
        response = self.client.get("/api/v1/menu/non-existent-menu")
        self.assertEqual(response.status_code, 404)
