"""
Module Description:
This module contains views controlling User and Data workflows. Specifically, these workflows interact with MongoDB for data storage and Django's authentication system and Postgres for user management.
"""
from .mongo_models import data_collection
from django.http import JsonResponse
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserRegisterSerializer, UserLoginSerializer
from .serializers import CustomTokenObtainPairSerializer
from .validations import custom_validation, validate_email, validate_password
from leasepeek.readers.xlsx import read_xlsx
from bson.objectid import ObjectId
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Token Authentication
class CustomTokenObtainPairView(TokenObtainPairView):
	""" 
	Custom token view that provides a way to obtain JWT token pairs (access + refresh) using custom serialization.
	"""
	serializer_class = CustomTokenObtainPairSerializer

##### USERS
class RegisterUserView(APIView):
	"""
	View for registering a new user. 
	This view validates the provided data, then registers a new user and generates an access token for them.
	"""
	def post(self, request):
		logger.info("Register User POST request initiated.")
		try:
			# Validate incoming user data
			clean_data = custom_validation(request.data)

		 	# If validation is successful, log the event.
			logger.info("User data validated successfully.")

			# Serialize the cleaned data for user registration
			serializer = UserRegisterSerializer(data=clean_data)

			# If the serialized data is valid, create a user and generate tokens
			if serializer.is_valid(raise_exception=True):
				user = serializer.create(clean_data)
				# Event log
				logger.info(f"User created successfully: {user.username}")
				if user:
					token_serializer = CustomTokenObtainPairSerializer()
					refresh = token_serializer.get_token_for_user(user)
					return Response({
					'refresh': str(refresh),
					'access': str(refresh.access_token),
					**serializer.data
				}, status=status.HTTP_201_CREATED)
		except ValidationError as e:
			logger.warning(f"Validation error during user registration: {e}")
			return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)		
		
		except Exception as e:
            # Log any other exceptions that occur.
			logger.error(f"An unexpected error occurred: {e}", exc_info=True)
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
	"""
	View for user login.
	This view validates the provided credentials, logs the user in, and generates an access token.
	"""
	def post(self, request):
		data = request.data
		
		# Validate user's email and password
		try:
			validate_email(data)
			validate_password(data)
		except ValidationError as e:
			return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
		
		# Serialize and check user login credentials
		serializer = UserLoginSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.check_user(data)
			login(request, user)

			# Generate tokens for the logged-in user
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

##### DATA
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def process_excel_data(request):
	"""
	View to process and store data from an Excel file.
	This view reads the uploaded Excel file, convers it to a DataFrame, and then stores it in MongoDB.
	"""
	user_id = request.user.user_id

	# Check if file is attached to the request
	if 'file' in request.FILES:
		file_obj = request.FILES['file']
		file_name = file_obj.name

		# Process the attached file and store its data in MongoDB
		try:
			data_frame = pd.read_excel(file_obj, header=None)
			unit_data = read_xlsx(data_frame, user_id, file_name)
			result = data_collection.insert_one(unit_data)
			return JsonResponse({"message": "Excel file processed successfully.", "objectId": str(result.inserted_id)})
		except Exception as e:
			print(f"Error processing excel file: {e}")
			return JsonResponse({"message": "Error processing excel file."})

	return JsonResponse({"message": "Invalid request method."})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def read_user_data(request):
	"""
	View to retrieve basic building data for the authenticated user.
	"""
	user_id = request.user.user_id
	cursor = data_collection.find({'user_id': user_id})
	basic_data = ['location', 'date', 'asOf', 'vacancy', 'floorplans', 'totalUnits']
	results = []
	for item in cursor:
		data = {k: item[k] for k in basic_data if k in item}
		data['objectId'] = str(item['_id'])
		results.append(data)
	return JsonResponse({"data": results, "message": "Request for basic building data received."})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def read_excel_data(request):
	"""
	View to retriee data from MongoDB based on an objectId.
	"""
	user = request.user.user_id
	object_id = request.GET.get('objectId', None)
	cursor = data_collection.find({
		'user_id': user,
		'_id': ObjectId(object_id)
	})
	results = [{k: v for k, v in item.items() if k != '_id'} for item in cursor]
	return JsonResponse(results, safe=False)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_property(request):
	"""
	View to delete a specific property data based on objectId.
	"""
	object_id = request.GET.get('objectId', None)
	data_collection.delete_one({"_id": ObjectId(object_id)})
	return JsonResponse({"message": "Property data deleted."})