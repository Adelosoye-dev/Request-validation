from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

auth_urls = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/reset', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

urlpatterns = auth_urls + [
    path('', include(router.urls)),
] 