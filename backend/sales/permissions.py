from rest_framework import permissions

class SalePermission(permissions.BasePermission):
    """
    Controla las acciones del módulo de Ventas según el rol del usuario.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Ver todas las ventas → todos los roles autenticados
        if view.action in ["list", "retrieve"]:
            return True

        # Crear ventas manualmente → manager o admin
        if view.action == "create":
            return user.role in ["manager", "admin"]

        # Actualizar estado o agregar pagos → vendedor, manager o admin
        if view.action in ["update", "partial_update", "add_payment", "mark_delivered"]:
            return user.role in ["vendedor", "manager", "admin"]

        # Cerrar venta / generar factura → solo manager o admin
        if view.action in ["mark_closed"]:
            return user.role in ["manager", "admin"]

        # Borrar ventas → solo admin
        if view.action == "destroy":
            return user.role == "admin"

        return False

    def has_object_permission(self, request, view, obj):
        """Permiso adicional a nivel de objeto."""
        user = request.user

        # Admin y soporte pueden todo
        if user.role in ["admin", "soporte"]:
            return True

        # Los vendedores solo pueden ver/modificar ventas de su empresa
        if hasattr(user, "company") and hasattr(obj, "quotation"):
            return obj.quotation.company == user.company

        return False
