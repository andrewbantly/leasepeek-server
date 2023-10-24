"""
Validation Module for leasepeek_backend Project.

This module contains custom validation functions used to ensure the integrity and correctness of user data during operations such as registration. The validators in this module check for the validity of user inputs such as email, username, and password.

Functions:
    - custom_validation(data): Comprehensive validation function that checks the 'email', 'username', and 'password' fields in the provided data. It performs checks for existence, uniqueness (for email), and compliance with defined standards (e.g., minimum password length).
    - validate_email(data): Validates the 'email' field in the provided data, ensuring it is non-empty.
    - validate_username(data): Validates the 'username' field in the provided data, ensuring it is non-empty.
    - validate_password(data): Validates the 'password' field in the provided data, ensuring it is non-empty.
"""

from django.core.exceptions import ValidationError  
from django.contrib.auth import get_user_model  
from django.core.validators import validate_email as validate_email_format

# Getting the user model currently active
UserModel = get_user_model()  

def custom_validation(data):
    """
    The custom_validation function takes a dictionary `data` as input and validates its 'email', 'username', and 'password' fields. 
    """

    # Stripping whitespace from the 'email', 'username', and 'password' fields
    email = data['email'].strip()  
    username = data['username'].strip()
    password = data['password'].strip()

    # Validate email format
    if email:
        try:
            validate_email_format(email)
        except ValidationError:
            raise ValidationError('Invalid email format')

    # Checking if the 'email' field is empty or if a user already exists with this email
    if not email or UserModel.objects.filter(email=email).exists():
        # Raising a ValidationError if the email is invalid
        raise ValidationError('Choose another email.')  

    # Checking if the 'password' field is empty or if the password is less than 8 characters long
    if not password or len(password) < 8:
        # Raising a ValidationError if the password is invalid
        raise ValidationError('Choose another password, min 8 characters.')  

    # Checking if the 'username' field is empty
    if not username:
        # Raising a ValidationError if the username is invalid
        raise ValidationError('choose another username')  

    # Returning the data if it passes all the validation checks
    return data  


def validate_email(data):
    """
    The validate_email function takes a dictionary `data` as input and validates its 'email' field.
    """

    # Stripping whitespace from the 'email' field in the input data
    email = data['email'].strip()

    # Validate email format
    if email:
        try:
            validate_email_format(email)
        except ValidationError:
            raise ValidationError('Invalid email format')

    # Raising a ValidationError if the email field is empty
    if not email:
        raise ValidationError('an email is needed')  

    # Returning True if the email passes the validation check
    return True  

def validate_username(data):
    """
    The validate_username function takes a dictionary `data` as input and validates its 'username' field.
    """

    # Stripping whitespace from the 'username' field in the input data
    username = data['username'].strip()  

    if not username:
        # Raising a ValidationError if the username field is empty
        raise ValidationError('choose another username')  

    # Returning True if the username passes the validation check
    return True  

def validate_password(data):
    # The validate_password function takes a dictionary `data` as input and validates its 'password' field.

    # Stripping whitespace from the 'password' field in the input data
    password = data['password'].strip()  

    if not password:
        # Raising a ValidationError if the password field is empty
        raise ValidationError('a password is needed')  

    # Returning True if the password passes the validation check
    return True  
