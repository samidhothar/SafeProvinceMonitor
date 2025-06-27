"""
URL configuration for accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Web interface URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # API URLs
    path('api/login/', views.LoginView.as_view(), name='api_login'),
    path('api/register/', views.RegisterView.as_view(), name='api_register'),
    path('api/logout/', views.LogoutView.as_view(), name='api_logout'),
    path('api/profile/', views.ProfileView.as_view(), name='api_profile'),
    path('api/change-password/', views.ChangePasswordView.as_view(), name='api_change_password'),
    path('api/auth-status/', views.check_auth_status, name='api_auth_status'),
]
