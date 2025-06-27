"""
Unit tests for accounts app.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='ADMIN',
            department='Health',
            district='Lahore'
        )
    
    def test_profile_creation(self):
        """Test profile creation."""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.role, 'ADMIN')
        self.assertEqual(self.profile.department, 'Health')
        self.assertEqual(self.profile.district, 'Lahore')
    
    def test_profile_properties(self):
        """Test profile properties."""
        self.assertTrue(self.profile.is_admin)
        self.assertFalse(self.profile.is_public)
        self.assertTrue(self.profile.can_edit_projects)
        self.assertTrue(self.profile.can_view_financial_data)


class LoginViewTest(TestCase):
    """Test cases for login view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user, role='PUBLIC')
    
    def test_login_page_loads(self):
        """Test login page loads successfully."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')
    
    def test_valid_login(self):
        """Test valid login credentials."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_invalid_login(self):
        """Test invalid login credentials."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')


class LoginAPITest(APITestCase):
    """Test cases for login API."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user, role='PUBLIC')
    
    def test_api_login_success(self):
        """Test successful API login."""
        url = reverse('accounts:api_login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
    
    def test_api_login_invalid_credentials(self):
        """Test API login with invalid credentials."""
        url = reverse('accounts:api_login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegisterAPITest(APITestCase):
    """Test cases for registration API."""
    
    def test_api_register_success(self):
        """Test successful API registration."""
        url = reverse('accounts:api_register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'role': 'PUBLIC'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        
        # Verify user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'PUBLIC')
    
    def test_api_register_password_mismatch(self):
        """Test API registration with password mismatch."""
        url = reverse('accounts:api_register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'role': 'PUBLIC'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthStatusAPITest(APITestCase):
    """Test cases for auth status API."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user, role='ADMIN')
        self.token = Token.objects.create(user=self.user)
    
    def test_auth_status_authenticated(self):
        """Test auth status for authenticated user."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('accounts:api_auth_status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])
        self.assertIsNotNone(response.data['user'])
    
    def test_auth_status_unauthenticated(self):
        """Test auth status for unauthenticated user."""
        url = reverse('accounts:api_auth_status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['authenticated'])
        self.assertIsNone(response.data['user'])
