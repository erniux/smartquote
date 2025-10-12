from django.db import models

class Product(models.Model):
    name = models.CharField("Nombre", max_length=100)
    description = models.TextField("Descripción", blank=True, null=True)
    price = models.DecimalField("Precio base", max_digits=10, decimal_places=2)
    dynamic_price_source = models.CharField(
        "Fuente de precio externo", max_length=50, blank=True, null=True
    )
    margin = models.DecimalField("Margen (%)", max_digits=5, decimal_places=2, default=0)
    unit = models.CharField("Unidad", max_length=50, default="pieza")
    image = models.ImageField("Imagen", upload_to="uploads/products/", blank=True, null=True)
    metal_symbol = models.CharField(
        "Símbolo del metal (opcional)",
        max_length=20,
        blank=True,
        null=True,
        help_text="Ejemplo: ALU, XCO, XCU, IRON"
    )
    created_at = models.DateTimeField("Creado el", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado el", auto_now=True)

    def update_dynamic_price(self):
        """Actualiza el precio si tiene fuente externa"""
        from services.api_clients import get_metal_price
        if self.dynamic_price_source:
            new_price = get_metal_price(self.dynamic_price_source)
            if new_price:
                self.price = new_price
                self.save()
    
    def update_price_from_metal(self):
        """
        Si el producto tiene un símbolo de metal asignado, 
        actualiza su precio automáticamente con el último valor guardado.
        """
        if not self.metal_symbol:
            return None

        from services.models import MetalPrice
        try:
            metal = MetalPrice.objects.filter(symbol=self.metal_symbol).order_by("-last_updated").first()
            if metal:
                old_price = self.price
                self.price = Decimal(metal.price_usd)
                self.save()
                return f"Precio actualizado de {old_price} → {self.price} USD"
        except Exception as e:
            print(f"⚠️ Error al actualizar precio de {self.name}: {e}")
            return None
   
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.name
