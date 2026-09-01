from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For OTP authentication
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['mobile']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def generate_otp(self):
        import random
        self.otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.otp_generated_at = timezone.now()
        self.save()
        return self.otp_code
    
    def verify_otp(self, otp):
        if not self.otp_code or not self.otp_generated_at:
            return False
        if timezone.now() > self.otp_generated_at + timezone.timedelta(minutes=10):
            return False
        return self.otp_code == otp

class UserGroup(models.Model):
    """Model to track group membership and admin privileges"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_groups'
        unique_together = ['user']  # One group for now, can be extended for multiple groups
