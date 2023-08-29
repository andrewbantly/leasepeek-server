from django.shortcuts import render
from .models import user_collection
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from rest_framework import permissions, status
from .validations import custom_validation, validate_email, validate_password
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.parsers import FileUploadParser
import openpyxl
# from .forms import DataForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import SessionAuthentication
import pandas as pd
from leasepeek.readers.xlsx_reader import read_rentroll
# from .serializer_unit import UnitSerializer

###### USERS 

class UserRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request):
		clean_data = custom_validation(request.data)
		serializer = UserRegisterSerializer(data=clean_data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.create(clean_data)
			if user:
				return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = (SessionAuthentication,)
	def post(self, request):
		data = request.data
		assert validate_email(data)
		assert validate_password(data)
		serializer = UserLoginSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.check_user(data)
			login(request, user)
			return Response(serializer.data, status=status.HTTP_200_OK)

class UserLogout(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)

class UserView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (SessionAuthentication,)
	def get(self, request):
		serializer = UserSerializer(request.user)
		return Response({'user': serializer.data}, status=status.HTTP_200_OK)

###### DATA 

@csrf_exempt
def excel_data(request):
	if request.method == 'POST':
		print("EXCEL DATA POST REQUEST RECEIVED")
		if 'file' in request.FILES:
			file_obj = request.FILES['file']
			try:
				data_frame = pd.read_excel(file_obj)
				data = read_rentroll(data_frame)
				rentroll_units = data[1]["Tenants"]
				# for unit in rentroll_units:
				# 	UnitSerializer.create(unit)
				rentroll_background = data[0]
				rentroll_summary_groups = data[2]
				rentroll_summary_charges = data[3]
				return JsonResponse({"message": "Excel file processed successfully."})
			except Exception as e:
				print(f"Error processing excel file: {e}")
				return JsonResponse({"message": "Error processing excel file."})
		else:
			return JsonResponse({"message": "No file attached."})
	return JsonResponse({"message": "Invalid request method."})

# TO BE FIXED LATER. looking for support to fix issue with Django's Rest Frameworks authorization and permissions.
class UploadExcelView(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = (SessionAuthentication,)
	def post(self, request):
		return Response({"message": "Reached the excel upload view"}, status=200)

def index(request):
    return HttpResponse("<h1>App is running...</h1>")

def add_user(request):
    records = {
        "username": "Andrew",
        "email": "andrew@dogdad.com"
    }
    user_collection.insert_one(records)
    return HttpResponse("New user added")

def get_all_users(request):
    users = user_collection.find()
    return HttpResponse(users)