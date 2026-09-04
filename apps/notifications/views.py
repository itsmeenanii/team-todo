from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from .models import Reminder, Notification
from .serializers import (
    ReminderSerializer, ReminderCreateSerializer, 
    NotificationSerializer
)
from .services import send_reminder, send_notification

class ReminderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReminderSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Reminder.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver', 'task')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReminderCreateSerializer
        return ReminderSerializer
    
    def perform_create(self, serializer):
        reminder = serializer.save(sender=self.request.user, status='pending')
        send_reminder(reminder)
        send_notification(
            user=reminder.receiver,
            title="Task Reminder",
            message=f"{reminder.sender.get_full_name()} reminded you to complete: {reminder.task.title}",
            notification_type='reminder',
            related_task=reminder.task
        )
    
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        reminder = self.get_object()
        if reminder.sender != request.user:
            return Response(
                {'error': 'You can only resend your own reminders'},
                status=status.HTTP_403_FORBIDDEN
            )
        reminder.status = 'pending'
        reminder.save()
        send_reminder(reminder)
        return Response({'message': 'Reminder resent successfully'})

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_read()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True, read_at=timezone.now())
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
