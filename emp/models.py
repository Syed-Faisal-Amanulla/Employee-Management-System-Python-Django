from email.policy import default
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User

class Emp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    name = models.CharField(max_length=100)
    emp_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    department = models.CharField(max_length=50)
    working = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
