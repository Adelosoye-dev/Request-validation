from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q, Max, Prefetch
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
import jwt
from datetime import datetime, timedelta

from .models import Post, Like, Conversation
from .serializers import (
    UserSerializer, UserUpdateSerializer, ChangePasswordSerializer,
    PostSerializer, LikeSerializer, ConversationSerializer,
    ConversationGroupSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

@permission_classes([AllowAny])
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        # print("Raw request data:", request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        # return Response({'jwt': "Okay o"}, status=200)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def change_password(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": "Wrong password."}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password updated successfully"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if query:
            users = self.queryset.filter(
                Q(email__icontains=query) |
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data)
        return Response([])

class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                
                # In a real application, send this via email
                reset_url = f"frontend_url/reset-password?token={token}"
                send_mail(
                    'Password Reset Request',
                    f'Click here to reset your password: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                return Response({"message": "Password reset email has been sent."})
            except User.DoesNotExist:
                return Response({"message": "If this email exists, a password reset link has been sent."})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = serializer.validated_data['token']
                # Verify token and get user
                # Implementation depends on your token strategy
                user = User.objects.get(id=1)  # Replace with actual user lookup
                
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                return Response({"message": "Password has been reset successfully."})
            except Exception as e:
                return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )
        
        if not created:
            like.delete()
            return Response({"message": "Post unliked"})
        
        return Response({"message": "Post liked"})

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def grouped_messages(self, request):
        # Get all conversations for the current user
        conversations = self.get_queryset()
        
        # Get unique users the current user has conversed with
        user_conversations = {}
        
        for conv in conversations:
            other_user = conv.receiver if conv.sender == request.user else conv.sender
            
            if other_user.id not in user_conversations:
                user_conversations[other_user.id] = {
                    'user': other_user,
                    'messages': [],
                    'last_message_timestamp': conv.timestamp
                }
            
            user_conversations[other_user.id]['messages'].append(conv)
            if conv.timestamp > user_conversations[other_user.id]['last_message_timestamp']:
                user_conversations[other_user.id]['last_message_timestamp'] = conv.timestamp
        
        # Sort conversations by last message timestamp
        sorted_conversations = sorted(
            user_conversations.values(),
            key=lambda x: x['last_message_timestamp'],
            reverse=True
        )
        
        serializer = ConversationGroupSerializer(sorted_conversations, many=True)
        return Response(serializer.data)
