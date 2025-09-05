from rest_framework.permissions import BasePermission
from .graph_nodes import UserNode, GroceryNode

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"

def user_is_responsible_for_grocery(django_user_id: int, grocery_uid: str) -> bool:
    try:
        user = UserNode.nodes.get(user_id=str(django_user_id))
        grocery = GroceryNode.nodes.get(uid=grocery_uid)
    except (UserNode.DoesNotExist, GroceryNode.DoesNotExist):
        return False
    return user.responsible_for.is_connected(grocery)

class CanModifyGroceryOrItems(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "ADMIN":
            return True
        grocery_uid = view.kwargs.get("grocery_uid") or view.kwargs.get("uid")
        if not grocery_uid:
            return False
        return user_is_responsible_for_grocery(request.user.id, grocery_uid)
