from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Añadir 'rut' a los campos mostrados en admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('rut',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {'fields': ('rut',)}),
    )
    list_display = ('username', 'email', 'rut', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'rut')
