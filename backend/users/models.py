from django.contrib.auth.models import AbstractUser
from django.db import models
from companies.models import Company 

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("soporte", "Soporte"),
        ("vendedor", "Vendedor"),
        ("supervisor", "Supervisor"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="vendedor"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
