from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Client, AgentImmobilier

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'nom', 'prenom', 'type', 'is_staff', 'is_active']
    list_filter = ['type', 'is_staff', 'is_active']
    search_fields = ['email', 'nom', 'prenom']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('nom', 'prenom', 'telephone', 'type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_creation')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2', 'nom', 'prenom', 'type', 'telephone')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['email', 'nom', 'prenom', 'date_creation']
    search_fields = ['email', 'nom', 'prenom']
    ordering = ['email']
    # You might want to customize the fields shown based on Client-specific fields later

@admin.register(AgentImmobilier)
class AgentImmobilierAdmin(admin.ModelAdmin):
    list_display = ['email', 'nom', 'prenom', 'date_creation']
    search_fields = ['email', 'nom', 'prenom']
    ordering = ['email']
    # You might want to customize the fields shown based on Agent-specific fields later
