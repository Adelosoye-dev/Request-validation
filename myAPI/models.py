from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=6)
    meta = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Portfolio(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='portfolio')
    position = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    years_of_experience = models.IntegerField()
    sector = models.CharField(max_length=100)
    skills = models.JSONField() 
    
    def __str__(self):
        return f"{self.person.first_name}'s Portfolio"
    