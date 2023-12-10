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
from bson.errors import InvalidId
import pandas as pd
import logging
import json
from leasepeek.data_updaters.basic_data_updates import update_basic_data
from leasepeek.data_updaters.floor_plan_details import update_floor_plan_data
from leasepeek.data_updaters.update_unit_statuses import update_unit_statuses
from leasepeek.data_updaters.charge_code_types import update_charge_code_types

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
			logger.info("Register User data validated.")

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
			return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)		
		
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
		logger.info("Login User POST request initiated.")
		data = request.data
		try:
			# Validate user's email and password
			validate_email(data)
			validate_password(data)
			logger.info("Login User data validated.")

		
			# Serialize and check user login credentials
			serializer = UserLoginSerializer(data=data)
			if serializer.is_valid(raise_exception=True):
				user = serializer.check_user(data)
				login(request, user)
				logger.info(f"User login successful: {user.username}")
				# Generate tokens for the logged-in user
				token_serializer = CustomTokenObtainPairSerializer()
				refresh = token_serializer.get_token_for_user(user)
				access_token = str(refresh.access_token)
				response_data = {
					'refresh': str(refresh),
					'access': access_token,
					'username': user.username,
					'email': user.email
					}
				return Response(response_data, status=status.HTTP_200_OK)
		except ValidationError as e:
			logger.warning(f"Validation error during user login: {e}")
			return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
		
		except Exception as e:
            # Log any other exceptions that occur.
			logger.error(f"An unexpected error occurred: {e}", exc_info=True)
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
	logger.info(f"User {request.user.username} initiated a process data POST request.")
	user_id = request.user.user_id

	# Check if file is attached to the request
	if 'file' in request.FILES:
		file_obj = request.FILES['file']
		file_name = file_obj.name
		logger.info(f"Received file '{file_name}' for processing.")

		# Check if file extension is xlsx
		if file_name.endswith('.xlsx'):
			# Process the attached file and store its data in MongoDB
			try:
				data_frame = pd.read_excel(file_obj, header=None)
				unit_data = read_xlsx(data_frame, user_id, file_name)
				result = data_collection.insert_one(unit_data)
				logger.info(f"File '{file_name}' processed successfully.")
				return JsonResponse({"message": "Excel file processed successfully.", "objectId": str(result.inserted_id)}, status=status.HTTP_201_CREATED)
			except Exception as e:
				logger.error(f"Error processing excel file '{file_name}': {e}", exc_info=True)
				return JsonResponse({"message": "Error processing excel file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		else:
			logger.warning(f"Invalid file extension for file '{file_name}'.")
			return JsonResponse({"message": "Invalid file type. Only .xlsx files are allowed."}, status=400)

	logger.warning(f"User {request.user.username} made a process data request without a file.")
	return JsonResponse({"message": "No file was included in the request."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_excel_data(request):
	logger.info("Update Rent Roll Data request recieved.")
	try:
		data = json.loads(request.body.decode('utf-8'))
		form_type = data.get('form')
		match form_type:
			case 'basic':
				response_message = update_basic_data(data)
				return JsonResponse({'status': 'success', 'message': response_message}, status=status.HTTP_200_OK)
			case 'floorPlanDetails':
				response_message = update_floor_plan_data(data)
				return JsonResponse({'status': 'success', 'message': response_message}, status=status.HTTP_200_OK)
			case 'unitStatus':
				response_message = update_unit_statuses(data)
				return JsonResponse({'status': 'success', 'message': response_message}, status=status.HTTP_200_OK)
			case 'chargeCodes':
				response_message = update_charge_code_types(data)
				return JsonResponse({'status': 'success', 'message': response_message}, status=status.HTTP_200_OK)
			case 'renovations':
				response_message = 'success'
				return JsonResponse({'status': 'success', 'message': response_message}, status=status.HTTP_200_OK)
	except json.JSONDecodeError:
		return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
	except Exception as e:
		logger.error(f"Error processing request: {e}")
		return JsonResponse({'status': 'error', 'message': 'Error processing request'}, status=500)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def read_user_data(request):
	"""
	View to retrieve basic building data for the authenticated user.
	"""
	user_id = request.user.user_id
	cursor = data_collection.find({'user_id': user_id})

    # Check if cursor is empty
	first_document = next(cursor, None)
	if first_document is None:
		logger.warning("No data found for User ID: %s", user_id)
		return Response({"data": [], "message": "No building data found."}, status=status.HTTP_404_NOT_FOUND)
	else:
		# If there is at least one document, process the cursor
		basic_data = ['location', 'date', 'asOf', 'vacancy', 'floorplans', 'totalUnits', 'totalBalance', 'lossToLease']
		results = []
		for item in cursor:
			data_item = {k: item[k] for k in basic_data if k in item}
			data_item['objectId'] = str(item['_id'])
			results.append(data_item)
		logger.info("Basic building data retrieved for User ID: %s", user_id)
		return Response({"data": results, "message": "Basic building data successfully retrieved."}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def read_excel_data(request):
	"""
	View to retrieve data from MongoDB based on an objectId.
	"""
	user = request.user.user_id
	object_id = request.GET.get('objectId', None)
	if object_id is None:
		logger.error("No objectId provided for user: %s", user)
		return JsonResponse({"message": "No objectId provided."}, status=status.HTTP_400_BAD_REQUEST)
	try:
		object_id = ObjectId(object_id)
	except InvalidId as e:
		logger.error("Invalid ObjectId: %s", object_id)
		return JsonResponse({"message": "Invalid objectId format."}, status=status.HTTP_400_BAD_REQUEST)
	try:	
		cursor = data_collection.find({
			'user_id': user,
			'_id': ObjectId(object_id)
		})

		if not cursor:
			logger.error("Invalid ObjectId: %s", object_id)
			return JsonResponse({"message": "Data not found."}, status=status.HTTP_404_NOT_FOUND)

		results = [{k: v for k, v in item.items() if k != '_id'} for item in cursor]
		if not results:
			logger.warning("No data found for ObjectId: %s", object_id)
			return JsonResponse({"message": "Data not found."}, status=status.HTTP_204_NO_CONTENT)

		logger.info("Data retrieved successfully")
		return JsonResponse(results, safe=False, status=status.HTTP_200_OK)
	except Exception as e:
		logger.error("Error retrieving data for ObjectId: %s", object_id)
	return JsonResponse({"message": "Error retrieving data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_property(request):
	"""
	View to delete a specific property data based on objectId.
	"""
	try:
		object_id = request.GET.get('objectId', None)

		# Check if objectId was provided in the request	
		if not object_id:
			logger.error("No objectId provided for property deletion")
			return Response({"message": "objectId must be provided."}, status=status.HTTP_400_BAD_REQUEST)
		
		# Attempt to delete the property data
		result = data_collection.delete_one({"_id": ObjectId(object_id)})

		# If no document was found/deleted, return a 404 Not Found
		if result.deleted_count == 0:
			logger.warning("No property found with objectId: %s", object_id)
			return Response({"message": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

	  # If the delete operation was successful, return a 200 OK
		logger.info("Property data deleted for objectId: %s", object_id)
		return Response({"message": "Property data deleted."}, status=status.HTTP_200_OK)

	except InvalidId:
        # Handle the case where the objectId provided is not valid
		logger.error("Invalid objectId provided: %s", object_id)
		return Response({"message": "Invalid objectId format."}, status=status.HTTP_400_BAD_REQUEST)

	except Exception as e:
        # Log any unexpected errors
		logger.exception("An error occurred while deleting property data: %s", str(e))
		return Response({"message": "An error occurred while deleting property data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)