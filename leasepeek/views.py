from .mongo_models import data_collection
from django.http import JsonResponse
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegisterSerializer, UserLoginSerializer
from .validations import custom_validation, validate_email, validate_password
import pandas as pd
from leasepeek.readers.xlsx import read_xlsx
from bson.objectid import ObjectId
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from leasepeek.readers.basic_data_functions.get_basic_data import find_basic_data

class CustomTokenObtainPairView(TokenObtainPairView):
	serializer_class = CustomTokenObtainPairSerializer
	print("### Inside Custom View")

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def protected_view(request):
	...

###### USERS

class RegisterUserView(APIView):
	def post(self, request):
		clean_data = custom_validation(request.data)
		serializer = UserRegisterSerializer(data=clean_data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.create(clean_data)
			if user:
				token_serializer = CustomTokenObtainPairSerializer()
				refresh = token_serializer.get_token_for_user(user)
				return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                **serializer.data
            }, status=status.HTTP_201_CREATED)
		return Response(status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        data = request.data
        try:
            validate_email(data)
            validate_password(data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(data)
            login(request, user)
            token_serializer = CustomTokenObtainPairSerializer()
            refresh = token_serializer.get_token_for_user(user)
            access_token = str(refresh.access_token)
            response_data = {
                'refresh': str(refresh),
                'access': access_token,
                'username': user.username,
                **serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

###### DATA 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_excel_data(request):
	user = request.user
	if request.method == 'POST':
		user_id = user.user_id
		if 'file' in request.FILES:
			file_obj = request.FILES['file']
			try:
				data_frame = pd.read_excel(file_obj, header=None)
				unit_data = read_xlsx(data_frame, user_id)
				# result = data_collection.insert_one(unit_data)
				# return JsonResponse({"message": "Excel file processed successfully.", "objectId": str(result.inserted_id)})
				return JsonResponse({"message": "Temp return message."})
			except Exception as e:
				print(f"Error processing excel file: {e}")
				return JsonResponse({"message": "Error processing excel file."})
		else:
			return JsonResponse({"message": "No file attached."})
	return JsonResponse({"message": "Invalid request method."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def read_user_data(request):
	user_id = request.user.user_id
	cursor = data_collection.find({'user_id': user_id})
	basic_data = find_basic_data(cursor)
	return JsonResponse({"data": basic_data, "message": "Request for basic building data received."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def read_excel_data(request):
	user = request.user.user_id
	object_id = request.GET.get('objectId', None)
	print("### User:", user)
	print("### Object ID:", object_id)

	cursor = data_collection.find({
		'user_id': user,
		'_id': ObjectId(object_id)
	})
	results = [{k: v for k, v in item.items() if k != '_id'} for item in cursor]
	return JsonResponse(results, safe=False)
