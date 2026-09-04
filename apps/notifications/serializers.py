from rest_framework import serializers
from .models import Reminder, Notification

class ReminderSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.get_full_name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = Reminder
        fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 
                  'task', 'task_title', 'message', 'reminder_type', 'status', 
                  'sent_at', 'created_at', 'updated_at']
        read_only_fields = ['sender', 'status', 'sent_at', 'created_at', 'updated_at']

class ReminderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['receiver', 'task', 'message', 'reminder_type']
    
    def validate(self, data):
        if data['receiver'] == self.context['request'].user:
            raise serializers.ValidationError("You cannot send a reminder to yourself")
        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 
                  'related_task', 'is_read', 'read_at', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
