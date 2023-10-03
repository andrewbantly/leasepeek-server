from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    ...
    def get_token_for_user(self, user):
        token = RefreshToken.for_user(user)
        token['username'] = user.username
        return token


User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('email', 'username')
	def create(self, clean_data):
		user_obj = User.objects.create_user(email=clean_data['email'], password=clean_data['password'], username=clean_data['username'])
		user_obj.username = clean_data['username']
		user_obj.save()
		return user_obj

class UserLoginSerializer(serializers.Serializer):
	class Meta:
		model = User
		fields = ('email', 'username')
	email = serializers.EmailField()
	password = serializers.CharField()
	def check_user(self, clean_data):
		user = authenticate(username=clean_data['email'], password=clean_data['password'])
		if not user:
			raise ValidationError('user not found')
		return user

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('email', 'username')