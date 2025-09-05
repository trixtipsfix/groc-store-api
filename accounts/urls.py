from django.urls import path
from .views import AdminCreateView, SupplierCreateView, MeView, UserDetailAdminView, UserListAdminView

urlpatterns = [
    path("admins/", AdminCreateView.as_view(), name="create_admin"),
    path("suppliers/", SupplierCreateView.as_view(), name="create_supplier"),
    path("me/", MeView.as_view(), name="me"),
    path("users/", UserListAdminView.as_view(), name="admin_user_list"),
    path("users/<int:pk>/", UserDetailAdminView.as_view(), name="admin_user_detail")
]
