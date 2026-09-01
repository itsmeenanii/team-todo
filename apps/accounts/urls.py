from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet, AdminMemberViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')
router.register(r'admin/members', AdminMemberViewSet, basename='admin-members')

urlpatterns = [
    path('', include(router.urls)),
]
