from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'mobile', 'role', 'is_active', 'is_verified', 'fcm_token']
        read_only_fields = ['id', 'role', 'is_active', 'is_verified']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name', 'mobile']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    otp = serializers.CharField(required=False, max_length=6)
    
    def validate(self, data):
        if not data.get('email') and not data.get('mobile'):
            raise serializers.ValidationError("Email or mobile number is required")
        if not data.get('password') and not data.get('otp'):
            raise serializers.ValidationError("Password or OTP is required")
        return data

class OTPRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=True)

class OTPVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(required=True)
    otp = serializers.CharField(required=True, max_length=6)

class AdminMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'mobile', 'role', 'is_active']
        read_only_fields = ['id', 'email', 'role']

class MemberAddSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile', 'fcm_token']
