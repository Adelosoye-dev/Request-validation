import json
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def get_message(request):
    if request.method == 'GET':
        return JsonResponse({"status": "success", "message": "Hello, world!", "data": None}, status=200)
    return JsonResponse({"status": "error", "message": "Method not allowed", "data": None}, status=405)

@csrf_exempt
def person_endpoint(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            required_fields = {
                'first_name': str, 'last_name': str, 'email': str, 'gender': str, 'phone': str
            }
            errors = []

            for field, field_type in required_fields.items():
                if field not in data:
                    errors.append(f"{field} is required")
                elif not isinstance(data[field], field_type):
                    errors.append(f"{field} should be of type {field_type.__name__}")

            if 'email' in data and not validateEmail(data['email']):
                errors.append("Invalid email format")
            
            if 'phone' in data and not validate_phone(data['phone']):
                errors.append("Invalid phone number format")

            if errors:
                return JsonResponse({"status": "error", "message": "Validation errors", "data": errors}, status=422)

            request.session['person'] = data
            return JsonResponse({"status": "success", "message": "Person created successfully", "data": data}, status=201)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e), "data": None}, status=400)

    elif request.method == 'GET':
        person = request.session.get('person')
        if not person:
            return JsonResponse({"status": "error", "message": "Person not found", "data": None}, status=404)
        return JsonResponse({"status": "success", "message": "Person retrieved", "data": person}, status=200)

    elif request.method == 'DELETE':
        if 'person' in request.session:
            del request.session['person']
            return JsonResponse({"status": "success", "message": "Person deleted successfully", "data": None}, status=200)
        return JsonResponse({"status": "error", "message": "Person not found", "data": None}, status=404)
    
    return JsonResponse({"status": "error", "message": "Invalid HTTP method", "data": None}, status=405)

@csrf_exempt
def person_modify(request):
    if request.method == 'PATCH':
        try:
            person = request.session.get('person')
            if not person:
                return JsonResponse({"status": "error", "message": "Person not found", "data": None}, status=404)

            extra_fields = ['age', 'address', 'nationality', 'occupation']
            data = json.loads(request.body)
            errors = []
            
            for field in extra_fields:
                if field in person:
                    errors.append(f"{field} already exists and cannot be added")
            for item in data:
                if item not in extra_fields:
                    extra_fields_string = ', '.join(extra_fields)
                    errors.append(f"{item} should be either, {extra_fields_string}")
            if errors:
                return JsonResponse({"status": "error", "message": "Validation errors", "data": errors}, status=422)
            
            person.update({key: data[key] for key in extra_fields if key in data})
            request.session['person'] = person
            return JsonResponse({"status": "success", "message": "Person details updated successfully", "data": person}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e), "data": None}, status=400)

    elif request.method == 'PUT':
        try:
            person = request.session.get('person')
            if not person:
                return JsonResponse({"status": "error", "message": "Person not found", "data": None}, status=404)

            data = json.loads(request.body)
            errors = []
            for key, value in data.items():
                if key in person and not isinstance(value, type(person[key])):
                    errors.append(f"{key} should be of type {type(person[key]).__name__}")
            
            if errors:
                return JsonResponse({"status": "error", "message": "Validation errors", "data": errors}, status=422)
            
            person.update(data)
            request.session['person'] = person
            return JsonResponse({"status": "success", "message": "Person details modified successfully", "data": person}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e), "data": None}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid HTTP method", "data": None}, status=405)
