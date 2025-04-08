import json
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Person, Portfolio
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from myAPI.models import Person

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
def persons(request):
    if request.method == 'GET':
        persons = list(Person.objects.values())
        return JsonResponse({"status": "success", "message": "Persons retrieved", "data": persons}, status=200)
   
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if Person.objects.filter(email=data['email']).exists():
                return JsonResponse({"status": "error", "message": "Email already exists", "data": None}, status=400)
            if not validate_email(data['email']):
                return JsonResponse({"status": "error", "message": "Invalid email format", "data": None}, status=400)
            if Person.objects.filter(phone=data['phone']).exists():
                return JsonResponse({"status": "error", "message": "Phone number already exists", "data": None}, status=400)
            
            person = Person(email=data['email'], first_name=data['first_name'], last_name=data['last_name'], phone=data['phone'], gender=data['gender']
            )
            person.save()
            return JsonResponse({"status": "success", "message": "Person created successfully", "data": model_to_dict(person)}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e), "data": None}, status=400)
    
        
@csrf_exempt
def person_detail(request, pk):
    try:
        person = Person.objects.get(pk=pk)
    except Person.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Person not found", "data": None}, status=404)   
    if request.method == 'GET':
        # return JsonResponse({"status": "success", "message": "Person retrieved", "data": person}, status=200)
        return JsonResponse({
                "status": "success", "message": "Person updated successfully", "data": model_to_dict(person)}, status=200)
    elif request.method == 'DELETE':
        person.delete()
        return JsonResponse({"status": "success", "message": "Person deleted successfully", "data": None}, status=200)
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            person.first_name = data['first_name']
            person.last_name = data['last_name']
            person.email = data['email']
            person.phone = data['phone']
            person.gender = data['gender']
            person.save()
            # return JsonResponse({"status": "success", "message": "Person updated successfully", "data": person}, status=200)
            return JsonResponse({"status": "success", "message": "Person updated successfully", "data": model_to_dict(person)}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e), "data": None}, status=400)

@csrf_exempt
def create_portfolio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            person_id = data.get("person_id")
            person = Person.objects.get(pk=person_id)

            if hasattr(person, 'portfolio'):
                return JsonResponse({
                    "status": "error",
                    "message": "Portfolio already exists for this person.",
                    "data": None
                }, status=400)

            portfolio = Portfolio.objects.create(
                person=person,
                position=data['position'],
                profession=data['profession'],
                years_of_experience=data['years_of_experience'],
                sector=data['sector'],
                skills=data['skills'] 
            )

            return JsonResponse({
                "status": "success",
                "message": "Portfolio created successfully",
                "data": model_to_dict(portfolio)
            }, status=201)

        except Person.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Person not found.",
                "data": None
            }, status=404)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e),
                "data": None
            }, status=400)
        
@csrf_exempt
def all_portfolios(request):
    if request.method == 'GET':
        portfolios = Portfolio.objects.all()
        portfolio_list = [model_to_dict(p) for p in portfolios]
        return JsonResponse({
            "status": "success",
            "message": "All portfolios retrieved",
            "data": portfolio_list
        }, status=200)

@csrf_exempt
def person_portfolio_detail(request, pk):
    if request.method == 'GET':
        try:
            portfolio = Portfolio.objects.get(person_id=pk)
            return JsonResponse({
                "status": "success",
                "message": "Portfolio retrieved successfully",
                "data": model_to_dict(portfolio)
            }, status=200)
        except Portfolio.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Portfolio not found.",
                "data": None
            }, status=404)
    elif request.method == 'DELETE':
        portfolio.delete()
        return JsonResponse({"status": "success", "message": "Portfolio deleted successfully", "data": None}, status=200)
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            portfolio.position = data['position']
            portfolio.profession = data['profession']
            portfolio.years_of_experience = data['years_of_experience']
            portfolio.sector = data['sector']
            portfolio.skills = data['skills']
            portfolio.save()
   
            return JsonResponse({"status": "success", "message": "Portfolio updated successfully", "data": model_to_dict(portfolio)}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e), "data": None}, status=400)


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
