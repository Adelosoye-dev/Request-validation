from .models import User, Conversation, Post, Like
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'username', 'password', 'timestamp', 'bio', 'profile_image']
        extra_kwargs = {'password': {'write_only': True}}

    # def create(self, validated_data):
    #     user = User(**validated_data)
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user
    
class ConversationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    class Meta:
        model = Conversation
        fields = ['id', 'message', 'image', 'timestamp', 'sender', 'receiver']
        extra_kwargs = {'sender': {'read_only': True}, 'receiver': {'read_only': True}}
        

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True)
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'timestamp']
        extra_kwargs = {'user': {'read_only': True}, 'post': {'read_only': True}}
   

    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     post = validated_data['post']
    #     like, created = Like.objects.get_or_create(user=user, post=post)
    #     return like

class PostSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    parent_post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True, allow_null=True)
    class Meta:
        model = Post
        fields = ['id', 'user', 'parent_post', 'title', 'body', 'image', 'timestamp']
        extra_kwargs = {'user': {'read_only': True}, 'parent_post': {'read_only': True}}
        
