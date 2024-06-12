from django.urls import path, include
from rest_framework import routers
from .views import CustomerViewSet, AddressViewSet, CustomerCreateView, LoginView, ForgotPasswordView, VerifyCodeView, ResetPasswordView, CartViewSet

router = routers.DefaultRouter()
router.register(r'customer', CustomerViewSet, basename='customers')
router.register(r'customer/addresses', AddressViewSet, basename='addresses')
router.register(r'customer/cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', CustomerCreateView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]