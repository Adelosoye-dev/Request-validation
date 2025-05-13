from django.db import models
import hashlib
import secrets

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(null=True, blank=True)
    profile_image = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, raw_password):
        salt = secrets.token_hex(8)
        hash_object = hashlib.md5((salt + raw_password).encode())
        hashed_pw = hash_object.hexdigest()
        self.password = f'{salt}${hashed_pw}'

    def check_password(self, raw_password):
        salt, hashed_pw = self.password.split('$')
        hash_object = hashlib.md5((salt + raw_password).encode())
        return hashed_pw == hash_object.hexdigest()
    
class Conversation(models.Model):
    message = models.TextField()
    image = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')

    def __str__(self):
        return f"Conversation by {self.user.username} at {self.timestamp}"
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    parent_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='quotes')
    title = models.CharField(max_length=100)
    body = models.TextField()
    image = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.username} at {self.timestamp}"
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"Like by {self.user.username} on post {self.post.id} at {self.timestamp}"