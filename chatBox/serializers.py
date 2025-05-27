from rest_framework import serializers
from .models import Conversation, Post, Like
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm=serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone', 'username', 'password', 'timestamp', 'bio', 'profile_image', 'password_confirm')
        extra_kwargs = {'first_name': {'required': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'): 
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'bio', 'profile_image')

class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs('new_password_confirm'): 
            raise serializers.ValidationError({"new_password": "Passwords don't match."})
        return attrs
    
class PasswordResetRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs('new_password_confirm'): 
            raise serializers.ValidationError({"new_password": "Passwords don't match."})
        return attrs

class ConversationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Conversation
        fields = ['id', 'message', 'image', 'timestamp', 'sender', 'receiver']
        read_only_fields = ('sender', 'timestamp')

class ConversationGroupSerializer(serializers.Serializer):
    user = UserSerializer()
    messages = ConversationSerializer(many=True)
    last_message_timestamp = serializers.DateTimeField()

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'timestamp']
        read_only_fields = ('user', 'timestamp')
   
    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     post = validated_data['post']
    #     like, created = Like.objects.get_or_create(user=user, post=post)
    #     return like

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    parent_post_details = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'parent_post', 'title', 'body', 'image', 'timestamp', 'likes_count', 'is_liked', 'parent_post_details']
        read_only_fields = ('user', 'timestamp')

        def get_likes_count(self, obj):
            return obj.likes.count()
        
        def get_is_liked(self, obj):
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                return obj.likes.filter(user=request.user).exists()
            return False
        
        def get_parent_post_details(self, obj):
            if obj.parent_post:
                return {
                    'id': obj.parent_post.id,
                    'body': obj.parent_post.body,
                    'user': {
                        'id': obj.parent_post.user.id,
                        'username': obj.parent_post.user.username
                    }
                }
            return None