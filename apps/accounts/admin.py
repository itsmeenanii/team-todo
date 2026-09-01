from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'mobile', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('mobile', 'role', 'is_verified', 'otp_code')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('mobile', 'role')}),
    )

admin.site.register(User, CustomUserAdmin)
