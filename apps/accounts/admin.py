from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserGroup

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'mobile', 'role', 'is_active', 'is_verified')
    list_filter = ('role', 'is_active', 'is_verified', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'mobile')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('mobile', 'role', 'is_verified', 'fcm_token', 'otp_code', 'otp_generated_at', 'last_login_ip')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('mobile', 'role', 'is_verified')}),
    )

class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_admin', 'joined_at')
    list_filter = ('is_admin', 'joined_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
