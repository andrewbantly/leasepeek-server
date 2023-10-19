"""
URL Configuration for the leasepeek_backend Django project.

This module defines the URL patterns for the leasepeek_backend project, effectively routing various URLs to their corresponding views or including additional URL configurations from different apps within the project.

The `urlpatterns` list is used to store all the URL patterns for the application.

Detailed URL routing:
- 'admin/': Default URL route for Django's admin site.
- 'user/': URL configuration from 'leasepeek.urls.user_urls', which handles user-specific operations.
- 'data/': URL configuration from 'leasepeek.urls.data_urls',  dealing with operations related to CRUD data processing.
- 'auth/': URL configuration from 'leasepeek.urls.auth_urls', handling authentication and authorization.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('leasepeek.urls.user_urls')),
    path('data/', include('leasepeek.urls.data_urls')),
    path('auth/', include('leasepeek.urls.auth_urls')),
]