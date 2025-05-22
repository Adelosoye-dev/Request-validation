from django.urls import path
from .views import register, UserLoginView

urlpatterns = [
    
    path('auth/register',register , name="register"), 
    path('auth/login', UserLoginView.as_view(), name="login"),               
    
]