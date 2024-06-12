from django.urls import path, include
from rest_framework import routers
from .views import ProductViewSet, CategoryViewSet, ImageViewSet, VariantViewSet

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'images', ImageViewSet, basename='images')
router.register(r'variants', VariantViewSet, basename='variants')

urlpatterns = [
    path('', include(router.urls)),
]