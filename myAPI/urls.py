from django.urls import path
from .views import get_message, person_endpoint, person_modify,persons,person_detail,create_portfolio,person_portfolio_detail,all_portfolios

urlpatterns = [
    path('message/', get_message, name="message"),                
    path('person', person_endpoint, name="person_endpoint"), 
    path('person/modify/<int:pk>', person_modify, name="person_modify"),
    path('persons', persons, name="persons"), 
    path('persons/<int:pk>', person_detail, name="person_detail") ,
    path('persons/portfolio', create_portfolio, name="create_portfolio"),
    path('persons/portfolios', all_portfolios, name="all_portfolios"),
    path('persons/<int:pk>/portfolio/', person_portfolio_detail, name="person_portfolio_detail"),
]
