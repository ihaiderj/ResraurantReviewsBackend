from django.urls import path
from ninja import NinjaAPI
from . import api

api_v1 = NinjaAPI()
api_v1.add_router("/menus/", api.router)

urlpatterns = [
    path("api/", api_v1.urls),
] 