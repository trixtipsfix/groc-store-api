from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN","Admin"
        SUPPLIER = "SUPPLIER","Supplier"

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=12, choices=Roles.choices, default=Roles.SUPPLIER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["email","name"]

    def __str__(self):
        return f"{self.name} ({self.email})"
