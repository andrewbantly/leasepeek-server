from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import json

class RegisterUserViewTest(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.user_data = {
            "username": "testuser",
            "password": "testpass",
            "email": "testuser@test.com"
        }
        self.User = get_user_model()

    def test_register_user_success(self):
        """
        Ensure we can register a new user with valid data.
        """
        response = self.client.post(self.register_url, self.user_data, format='json')
        user = self.User.objects.filter(email=self.user_data["email"]).first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.username, self.user_data["username"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        # Here, you might also want to check the response data for the tokens and ensure they're valid

    def test_register_user_existing_username(self):
        """
        Ensure we cannot register a user with an existing username.
        """
        self.User.objects.create_user(**self.user_data)
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'detail': ['Choose another email.']})  # Make sure this matches the error structure you're returning


    # You can add more methods here to test other failure cases (e.g., invalid email, short password, etc.)
