from django.shortcuts import render
from .models import user_collection
from django.http import HttpResponse
# Create your views here.

def index(request):
    return HttpResponse("<h1>App is running...</h1>")

def add_user(request):
    records = {
        "username": "Murphy",
        "email": "murphy@dog.co"
    }
    user_collection.insert_one(records)
    return HttpResponse("New user added")

def get_all_users(request):
    users = user_collection.find()
    return HttpResponse(users)

