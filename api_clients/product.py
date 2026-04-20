
from django.conf import settings
from .utils import APIClient

class ProductClientService(APIClient):
    def __init__(self, request):
        super().__init__(request, settings.PRODUCT_SERVICE_URL)

    def get(self, url, params=None, stream=False):
        return super().get(f"{url}", params=params, stream=stream)
    
    def post(self, url, data):
        return super().post(f"{url}", data)
    
    def put(self, url, data):
        return super().put(f"{url}", data)
    
    def patch(self, url, data):
        return super().patch(f"{url}", data)
    
    def delete(self, url):
        return super().delete(f"{url}")
