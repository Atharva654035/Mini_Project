from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    division = models.CharField(max_length=100)

    def __str__(self):
        return f"Profile for {self.user.username}"
