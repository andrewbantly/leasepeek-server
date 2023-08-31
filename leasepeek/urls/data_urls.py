from django.urls import path
from .. import views

urlpatterns = [
    path('upload', views.download_excel_data),
    path('read', views.read_excel_data),
    path('user', views.read_user_data),
]