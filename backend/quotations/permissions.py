from rest_framework import permissions

class QuotationPermission(permissions.BasePermission):
    """
    Controla los permisos de acuerdo al rol del usuario.
    """

    def has_permission(self, request, view):
        # Debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # Lectura siempre permitida
        if view.action in ["list", "retrieve"]:
            return True

        # Crear cotizaciones → vendedor, gerente o admin
        if view.action == "create":
            return request.user.role in ["vendedor", "manager", "admin"]

        # Para las acciones personalizadas (cancel, generate-sale)
        if view.action in ["cancel_quotation", "generate_sale"]:
            return request.user.role in ["manager", "admin"]

        # Actualizar / editar (solo borradores)
        if view.action in ["update", "partial_update"]:
            return request.user.role in ["vendedor", "manager", "admin"]

        # Borrar → solo admin
        if view.action == "destroy":
            return request.user.role == "admin"

        return False

    def has_object_permission(self, request, view, obj):
        """
        Controla permisos sobre objetos individuales.
        """
        user = request.user

        # Admin o soporte puede todo
        if user.role in ["admin", "soporte"]:
            return True

        # Solo puede modificar sus cotizaciones de su empresa
        if view.action in ["update", "partial_update", "cancel_quotation", "generate_sale"]:
            return obj.company == user.company

        return True
