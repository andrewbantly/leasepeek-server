"""
URL Configuration for user authentication views.

This module contains URL patterns associated with user operations, specifically registration and login. It maps URLs to the appropriate views that handle user authentication processes.

Available endpoints:
- 'user/register': Endpoint for user registration. Connects to the RegisterUserView for user sign-up processes.
- 'user/login': Endpoint for user login. Connects to the UserLoginView for existing user authentication.
"""

from django.urls import path
from .. import views

urlpatterns = [
    path('register', views.RegisterUserView.as_view(), name='register'),
    path('login', views.UserLoginView.as_view(), name='login'),
]
