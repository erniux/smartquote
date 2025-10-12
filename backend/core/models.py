from django.db import models

class Product(models.Model):
    name = models.CharField("Nombre", max_length=100)
    description = models.TextField("Descripción", blank=True, null=True)
    price = models.DecimalField("Precio base", max_digits=10, decimal_places=2)
    margin = models.DecimalField("Margen (%)", max_digits=5, decimal_places=2, default=0)
    unit = models.CharField("Unidad", max_length=50, default="pieza")
    image = models.ImageField("Imagen", upload_to="uploads/products/", blank=True, null=True)
    created_at = models.DateTimeField("Creado el", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado el", auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.name
