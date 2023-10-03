from .mongo_models import data_collection
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from .validations import custom_validation, validate_email, validate_password
import pandas as pd
from leasepeek.readers.xlsx import read_xlsx
from bson.objectid import ObjectId
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def protected_view(request):
    print("did something happen?")




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
def process_excel_data(request):
	user = request.user
	if request.method == 'POST' and user.is_authenticated:
		user_id = user.user_id
		if 'file' in request.FILES:
			file_obj = request.FILES['file']
			try:
				data_frame = pd.read_excel(file_obj, header=None)
				unit_data = read_xlsx(data_frame, user_id)
				result = data_collection.insert_one(unit_data)
				return JsonResponse({"message": "Excel file processed successfully.", "objectId": str(result.inserted_id)})
			except Exception as e:
				print(f"Error processing excel file: {e}")
				return JsonResponse({"message": "Error processing excel file."})
		else:
			return JsonResponse({"message": "No file attached."})
	return JsonResponse({"message": "Invalid request method."})

@csrf_exempt
def read_user_data(request):
    user_id = request.user.user_id
    cursor = data_collection.find({
        'user_id': user_id
    }, {'location': 1, 'date': 1})

    buildings_and_dates = [{
		'location': doc.get('location'), 
		'date': doc.get('date'),
		'objectId': str(doc.get('_id'))
		} for doc in cursor]

    return JsonResponse({"data": buildings_and_dates, "message": "Request for user building and date data received."})


@csrf_exempt
def read_excel_data(request):
	user = request.user
	object_id = request.GET.get('id', None)
	if request.method == 'GET' and user.is_authenticated:
		user_id = user.user_id
		cursor = data_collection.find({
			'user_id': user_id,
			'_id': ObjectId(object_id)
		})
		results = [{k: v for k, v in item.items() if k != '_id'} for item in cursor]
		return JsonResponse(results, safe=False)
	return JsonResponse({"message": "Invalid request method."})