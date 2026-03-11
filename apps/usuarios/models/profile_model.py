from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    rol = models.CharField(max_length=20, choices=[
        ('agricultor', 'Agricultor'),
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
    ], default='cliente')

    def __str__(self):
        return f"Profile of {self.user.username}"