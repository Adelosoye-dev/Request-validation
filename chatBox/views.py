from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
import json
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def validate_phone(phone):
    pattern = r'^\+?[0-9]{7,11}$'
    return re.match(pattern, phone)

def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def validatePassword(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            phone = data.get('phone')
            username = data.get('username')
            password = data.get('password')
            bio = data.get('bio')
            profile_image = data.get('profile_image')
            if not all([first_name, last_name, email, phone, username, password]):
                return JsonResponse({'error': 'All fields are required'}, status=422)
            if not validate_email(email):
                return JsonResponse({'error': 'Invalid email format'}, status=422)
            if not validate_phone(phone):
                return JsonResponse({'error': 'Invalid phone number format'}, status=400)
            if not validateEmail(email):
                return JsonResponse({'error': 'Invalid email format'}, status=422)
            if not validatePassword(password):
                return JsonResponse({'error': 'Password must be at least 8 characters long and contain both letters and numbers'}, status=422)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'error': 'Phone number already exists'}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                username=username,
                password=password,  
                bio=bio,
                profile_image=profile_image
            )
            user.set_password(password)  
            user.save()

            return JsonResponse({'message': 'User registered successfully!'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
       
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not all([username, password]):
                return JsonResponse({'error': 'All fields are required'}, status=422)
            
            user = User.objects.filter(username=username).first()
            if user and user.check_password(password):
                # Log in user to session
                return JsonResponse({'message': 'Login successful!'})
            else:
                return JsonResponse({'error': 'Invalid username or password'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)