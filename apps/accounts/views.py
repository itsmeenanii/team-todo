from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    OTPRequestSerializer, OTPVerifySerializer, AdminMemberSerializer,
    MemberAddSerializer, UserProfileUpdateSerializer
)
from .permissions import IsAdminUser
from apps.notifications.services import send_welcome_email

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_welcome_email(user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Registration successful. Please login.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user = None
        
        # Password login
        if data.get('password'):
            if data.get('email'):
                user = authenticate(request, username=data['email'], password=data['password'])
            elif data.get('mobile'):
                try:
                    user_obj = User.objects.get(mobile=data['mobile'])
                    user = authenticate(request, username=user_obj.email, password=data['password'])
                except User.DoesNotExist:
                    pass
        
        # OTP login
        elif data.get('otp'):
            try:
                user_obj = User.objects.get(mobile=data['mobile'])
                if user_obj.verify_otp(data['otp']):
                    user = user_obj
            except User.DoesNotExist:
                pass
        
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @action(detail=False, methods=['post'])
    def request_otp(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        mobile = serializer.validated_data['mobile']
        try:
            user = User.objects.get(mobile=mobile)
            if not user.is_active:
                return Response(
                    {'error': 'User account is inactive'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            otp = user.generate_otp()
            # In production, send OTP via SMS
            # send_otp_sms(mobile, otp)
            return Response({
                'otp': otp,  # Remove in production
                'message': 'OTP sent successfully'
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        mobile = serializer.validated_data['mobile']
        otp = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(mobile=mobile)
            if user.verify_otp(otp):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                })
            return Response(
                {'error': 'Invalid or expired OTP'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logged out successfully'})
        except Exception:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        if self.request.user.is_admin() and self.action in ['create', 'update', 'partial_update']:
            return AdminMemberSerializer
        return super().get_serializer_class()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_role(self, request, pk=None):
        if not request.user.is_admin():
            return Response(
                {'error': 'Only admins can update roles'},
                status=status.HTTP_403_FORBIDDEN
            )
        user = self.get_object()
        new_role = request.data.get('role')
        if new_role not in ['admin', 'member']:
            return Response(
                {'error': 'Invalid role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.role = new_role
        user.save()
        return Response(self.get_serializer(user).data)

class AdminMemberViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminMemberSerializer
    
    @action(detail=False, methods=['post'])
    def add_member(self, request):
        serializer = MemberAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user, created = User.objects.get_or_create(
            mobile=data['mobile'],
            defaults={
                'email': data.get('email', ''),
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'username': data['mobile'],
                'role': 'member'
            }
        )
        
        if not created:
            return Response(
                {'error': 'User already exists'},
                status=status.HTTP_409_CONFLICT
            )
        
        temp_password = User.objects.make_random_password()
        user.set_password(temp_password)
        user.save()
        send_welcome_email(user, temp_password)
        
        return Response({
            'user': AdminMemberSerializer(user).data,
            'temporary_password': temp_password
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        if user.role == 'admin':
            return Response(
                {'error': 'Cannot remove an admin'},
                status=status.HTTP_403_FORBIDDEN
            )
        user.is_active = False
        user.save()
        return Response({'message': 'Member removed successfully'})
    
    @action(detail=False, methods=['get'])
    def members(self, request):
        users = User.objects.filter(role='member', is_active=True)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def admins(self, request):
        users = User.objects.filter(role='admin', is_active=True)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
