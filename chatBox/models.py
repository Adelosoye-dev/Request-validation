from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
import json

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=15, unique=True)
    username = models.CharField(max_length=50, unique=True)
    bio = models.TextField(null=True, blank=True)
    profile_image = models.TextField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone', 'first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
  
class Conversation(models.Model):
    message = models.TextField()
    image = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    parent_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='quotes')
    title = models.CharField(max_length=100)
    body = models.TextField()
    image = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}'s post at {self.timestamp}"
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} likes {self.post}"