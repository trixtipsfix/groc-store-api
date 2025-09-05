from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["id","name","email","password","role","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.username = validated_data.get("name")
        user.set_password(password)
        user.save()
        return user

class UserAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "email", "role", "is_active", "updated_at"]
        read_only_fields = ["updated_at"]
        
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","name","email","role","created_at","updated_at"]
