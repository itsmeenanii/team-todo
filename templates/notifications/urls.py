from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReminderViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'reminders', ReminderViewSet, basename='reminders')
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
]
