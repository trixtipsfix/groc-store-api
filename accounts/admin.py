from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Profile",{"fields":("name","role")}),)
    list_display = ("id","name","email","role","is_active","is_staff")
    search_fields = ("name","email","username")
