from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre de la empresa")
    logo = models.ImageField(upload_to="uploads/companies/", blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
