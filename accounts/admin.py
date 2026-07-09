from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, CandidateProfile, EmployerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "username",
        "role",
        "is_active",
        "is_staff",
        "is_verified",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_verified",
    )

    search_fields = (
        "email",
        "username",
    )

    ordering = ("email",)


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)