from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Case, When, IntegerField, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Task, TaskStatus
from .serializers import (
    TaskSerializer, TaskStatusSerializer, TaskCreateSerializer,
    TaskUpdateStatusSerializer, TaskDashboardSerializer
)
from apps.accounts.models import User
from apps.accounts.permissions import IsAdminUser

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Get tasks the user can see
        if user.is_admin():
            tasks = Task.objects.all()
        else:
            # Personal tasks created by user OR group tasks assigned to user
            personal_tasks = Task.objects.filter(
                type='personal',
                created_by=user,
                is_active=True
            )
            group_tasks = Task.objects.filter(
                type='group',
                is_active=True,
                statuses__user=user
            ).distinct()
            tasks = personal_tasks | group_tasks
        
        # Filter by type if provided
        task_type = self.request.query_params.get('type')
        if task_type in ['personal', 'group']:
            tasks = tasks.filter(type=task_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            tasks = tasks.filter(assigned_date__gte=start_date)
        if end_date:
            tasks = tasks.filter(assigned_date__lte=end_date)
        
        return tasks.order_by('-assigned_date', 'created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        
        # If group task, create statuses for assigned users
        if task.type == 'group' and 'assigned_users' in serializer.validated_data:
            assigned_users = serializer.validated_data['assigned_users']
            for user_id in assigned_users:
                try:
                    user = User.objects.get(id=user_id, is_active=True)
                    TaskStatus.objects.get_or_create(task=task, user=user, defaults={'status': 'pending'})
                except User.DoesNotExist:
                    pass
        elif task.type == 'personal':
            # Create status for the creator
            TaskStatus.objects.get_or_create(task=task, user=self.request.user, defaults={'status': 'pending'})
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        task = self.get_object()
        serializer = TaskUpdateStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        status_obj, created = TaskStatus.objects.get_or_create(
            task=task,
            user=request.user,
            defaults={'status': 'pending'}
        )
        
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')
        
        if new_status == 'done':
            status_obj.mark_done()
        else:
            status_obj.mark_not_done()
        
        if notes:
            status_obj.notes = notes
            status_obj.save()
        
        return Response(TaskStatusSerializer(status_obj).data)
    
    @action(detail=True, methods=['get'])
    def statuses(self, request, pk=None):
        task = self.get_object()
        
        # Check if user has permission to view statuses
        if task.type == 'personal' and task.created_by != request.user:
            return Response(
                {'error': 'You do not have permission to view this task\'s statuses'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        statuses = task.statuses.all().select_related('user')
        serializer = TaskStatusSerializer(statuses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data with group task completion status"""
        if not request.user.is_admin():
            # Regular users see their own dashboard
            return self._get_user_dashboard(request.user)
        else:
            # Admin sees all users
            return self._get_admin_dashboard()
    
    def _get_user_dashboard(self, user):
        # Get today's group tasks
        today = timezone.now().date()
        group_tasks = Task.objects.filter(
            type='group',
            assigned_date=today,
            is_active=True
        )
        
        personal_tasks = Task.objects.filter(
            type='personal',
            created_by=user,
            is_active=True
        )
        
        # Get statuses
        task_data = []
        for task in group_tasks:
            status = TaskStatus.objects.filter(task=task, user=user).first()
            task_data.append({
                'task_id': task.id,
                'title': task.title,
                'type': task.type,
                'status': status.status if status else 'pending',
                'completed_at': status.completed_at if status else None
            })
        
        return Response({
            'user_id': user.id,
            'user_name': user.get_full_name(),
            'group_tasks': task_data,
            'personal_tasks': TaskSerializer(personal_tasks, many=True).data,
            'total_tasks': len(group_tasks) + personal_tasks.count(),
            'completed_tasks': len([t for t in task_data if t['status'] == 'done'])
        })
    
    def _get_admin_dashboard(self):
        today = timezone.now().date()
        group_tasks = Task.objects.filter(
            type='group',
            assigned_date=today,
            is_active=True
        )
        
        # Get all active users
        users = User
