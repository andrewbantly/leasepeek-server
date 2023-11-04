"""
URL Configuration for data-related operations.

This module defines the URL patterns associated with data processing functionalities, specifically those related to handling Excel rent roll data within the application. These URL routes are linked to views that execute the required operations, such as uploading, reading, or deleting data.

Available endpoints:
- 'data/upload': Maps to the `process_excel_data` view, where data from an uploaded Excel file is processed and stored in MongoDB.
- 'data/read': Routes to the `read_excel_data` view, which handles requests for retrieving and reading data originally stored from Excel files.
- 'data/user': Linked to the `read_user_data` view, this pattern deals with requests to fetch basic data specific to a user.
- 'data/delete': Connects to the `delete_property` view, enabling the removal of property records from the system.
"""

from django.urls import path
from .. import views

urlpatterns = [
    path('upload', views.process_excel_data, name='process_data'),
    path('read', views.read_excel_data, name='read_data'),
    path('user', views.read_user_data, name='read_user_data'),
    path('delete', views.delete_property, name='delete_property')
]
