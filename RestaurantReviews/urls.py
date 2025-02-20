"""
URL configuration for RestaurantReviews project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import RegisterView, CustomTokenObtainPairView, UserProfileView
from ninja import NinjaAPI
from menus.api import router as menus_router

# Customize admin site
admin.site.site_header = 'Restaurant Reviews Administration'
admin.site.site_title = 'Restaurant Reviews Admin Portal'
admin.site.index_title = 'Welcome to Restaurant Reviews Admin Portal'

api = NinjaAPI()
api.add_router("/menus/", menus_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/restaurants/', include('restaurants.urls')),
    path('api/', api.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
