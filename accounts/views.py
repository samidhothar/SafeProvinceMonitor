"""
Views for accounts app - authentication and user management.
"""
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import AuthenticationForm
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .serializers import (
    LoginSerializer, 
    RegisterSerializer, 
    UserSerializer, 
    ChangePasswordSerializer
)
from .models import UserProfile


class LoginView(APIView):
    """API view for user login."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Handle user login via API."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """API view for user registration."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Handle user registration via API."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """API view for user logout."""
    
    def post(self, request):
        """Handle user logout via API."""
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({
                'message': 'Token not found'
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """API view for user profile management."""
    
    def get(self, request):
        """Get current user profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Update current user profile."""
        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        
        if user_serializer.is_valid():
            user_serializer.save()
            
            # Update profile if provided
            if hasattr(request.user, 'profile') and 'profile' in request.data:
                profile_data = request.data['profile']
                for key, value in profile_data.items():
                    if hasattr(request.user.profile, key):
                        setattr(request.user.profile, key, value)
                request.user.profile.save()
            
            return Response(UserSerializer(request.user).data)
        
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """API view for changing user password."""
    
    def post(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            # Update token
            Token.objects.filter(user=request.user).delete()
            token = Token.objects.create(user=request.user)
            
            return Response({
                'token': token.key,
                'message': 'Password changed successfully'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Django template views
def login_view(request):
    """Handle user login via web interface."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout via web interface."""
    username = request.user.username
    logout(request)
    messages.info(request, f'You have been logged out successfully, {username}.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Display user profile page."""
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': getattr(request.user, 'profile', None)
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_auth_status(request):
    """Check authentication status."""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data
        })
    else:
        return Response({
            'authenticated': False,
            'user': None
        })
