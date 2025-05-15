from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'logement', 'emetteur', 'destinataire', 'date_envoi', 'lu')
    list_filter = ('lu', 'date_envoi', 'logement')
    search_fields = ('contenu', 'emetteur__email', 'destinataire__email', 'logement__titre')
    date_hierarchy = 'date_envoi'
    ordering = ('-date_envoi',)
    readonly_fields = ('date_envoi',)
    raw_id_fields = ('logement', 'emetteur', 'destinataire') # Use search popup for foreign keys
    fieldsets = (
        (None, {'fields': ('logement', 'emetteur', 'destinataire')}),
        ('Content', {'fields': ('contenu', 'lu')}),
        ('Date', {'fields': ('date_envoi',)}),
    )
