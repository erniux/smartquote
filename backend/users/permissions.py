from rest_framework import permissions

class IsCompanyMemberOrAdmin(permissions.BasePermission):
    """
    Permite el acceso si el usuario es admin/soporte o pertenece a la misma compañía que el objeto.
    """

    def has_permission(self, request, view):
        user = request.user

        # Si no está autenticado, denegar acceso
        if not user or not user.is_authenticated:
            return False

        # Admin o soporte → acceso completo
        if user.role in ["admin", "soporte"]:
            return True

        # Otros usuarios → verificar si la vista tiene filtro por compañía
        return hasattr(user, "company") and user.company is not None

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin y soporte tienen acceso a todo
        if user.role in ["admin", "soporte"]:
            return True

        # Si el objeto tiene campo "company", comparar
        if hasattr(obj, "company"):
            return obj.company == user.company

        # Si el objeto no tiene "company", denegar
        return False
