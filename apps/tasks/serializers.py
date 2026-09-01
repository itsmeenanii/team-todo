from rest_framework import serializers
from .models import Task, TaskStatus
from django.utils import timezone

class TaskSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'type', 'created_by', 'created_by_name',
                  'assigned_date', 'created_at', 'updated_at', 'is_active', 'completion_percentage']
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_completion_percentage(self, obj):
        if obj.type == 'personal':
            return None
        total = obj.statuses.count()
        if total == 0:
            return 0
        done = obj.statuses.filter(status='done').count()
        return round((done / total) * 100, 2)

class TaskStatusSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = TaskStatus
        fields = ['id', 'task', 'task_title', 'user', 'user_name', 'user_email',
                  'status', 'completed_at', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['task', 'user', 'created_at', 'updated_at']

class TaskCreateSerializer(serializers.ModelSerializer):
    assigned_users = serializers.ListField(child=serializers.IntegerField(), required=False)
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'type', 'assigned_date', 'assigned_users']
    
    def validate(self, data):
        if data.get('type') == 'group' and not data.get('assigned_users'):
            raise serializers.ValidationError("Group tasks require assigned users")
        return data

class TaskUpdateStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['done', 'not_done'])
    notes = serializers.CharField(required=False, allow_blank=True)

class TaskDashboardSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    task_id = serializers.IntegerField()
    task_title = serializers.CharField()
    status = serializers.CharField()
    completed_at = serializers.DateTimeField(allow_null=True)
