from django.db import models

# Create your models here.
class Person(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=6)
    meta = models.JSONField(default=dict)

    def _str_(self):
        return f"{self.first_name} {self.last_name}"
    
   