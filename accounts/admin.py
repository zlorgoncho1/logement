from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Client, AgentImmobilier
# from .forms import CustomUserCreationForm, CustomUserChangeForm # If you have custom admin forms

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # add_form = CustomUserCreationForm # Define if you have a custom creation form for admin
    # form = CustomUserChangeForm # Define if you have a custom change form for admin
    model = CustomUser

    list_display = ('email', 'nom', 'prenom', 'type', 'is_staff', 'is_active', 'kyc_verified')
    list_filter = ('type', 'is_staff', 'is_superuser', 'is_active', 'kyc_verified', 'date_creation')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('nom', 'prenom', 'telephone')}),
        (_('Permissions'), {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions',
        )}),
        (_('User Type & KYC'), {'fields': ('type', 'documents_kyc', 'kyc_verified')}), # Added KYC fields
        (_('Important dates'), {'fields': ('last_login', 'date_creation')}),
    )
    # For add form, if different fields are needed
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2', 'nom', 'prenom', 'telephone', 'type', 'is_staff', 'is_active', 'is_superuser'),
        }),
    )
    search_fields = ('email', 'nom', 'prenom')
    ordering = ('-date_creation', 'email')

    filter_horizontal = ('groups', 'user_permissions', 'documents_kyc') # Added documents_kyc here
    
    actions = ['activate_selected_agents', 'deactivate_selected_users']

    def activate_selected_agents(self, request, queryset):
        # Action to activate agent accounts and mark KYC as verified
        agents_updated = 0
        for user in queryset.filter(type=CustomUser.UserType.AGENT):
            user.is_active = True
            user.kyc_verified = True
            user.save()
            agents_updated += 1
        if agents_updated > 0:
            self.message_user(request, _("%(count)d agent accounts have been successfully activated and KYC verified.") % {'count': agents_updated})
        else:
            self.message_user(request, _("No agent accounts were selected or updated."), level=messages.WARNING)
    activate_selected_agents.short_description = _("Activate selected Agents & verify KYC")

    def deactivate_selected_users(self, request, queryset):
        # Generic deactivation, could also un-verify KYC if needed
        users_updated = queryset.update(is_active=False)
        # If you also want to mark KYC as unverified when deactivating agents:
        # for user in queryset.filter(type=CustomUser.UserType.AGENT):
        #     user.kyc_verified = False
        #     user.save()
        self.message_user(request, _("%(count)d users have been successfully deactivated.") % {'count': users_updated})
    deactivate_selected_users.short_description = _("Deactivate selected users")

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
