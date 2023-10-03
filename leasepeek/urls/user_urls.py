from django.urls import path
from .. import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
	path('register', views.RegisterUserView.as_view(), name='register'),
	path('login', views.UserLoginView.as_view(), name='login'),
]