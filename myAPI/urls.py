from django.urls import path
from .views import get_message, person_endpoint, person_modify,persons

urlpatterns = [
    path('message/', get_message, name="message"),                
    path('person', person_endpoint, name="person_endpoint"), 
    path('person/modify', person_modify, name="person_modify"),
    path('persons', persons, name="persons") 
]
