from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer, UserDetailSerializer
from .permissions import IsAdminRole
from .serializers import UserAdminUpdateSerializer

User = get_user_model()

class AdminCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdminRole]
    def perform_create(self, serializer):
        serializer.save(role="ADMIN")

class SupplierCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdminRole]
    def perform_create(self, serializer):
        serializer.save(role="SUPPLIER")

class MeView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

class UserDetailAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserAdminUpdateSerializer
    permission_classes = [IsAdminRole]

    # Prefer soft-delete of users in production
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

class UserListAdminView(generics.ListAPIView):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminRole]