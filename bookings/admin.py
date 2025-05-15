from django.contrib import admin
from .models import Reservation
# Inline for Paiement if needed in Reservation view
# from payment.admin import PaiementInline

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'logement', 'client', 'date_debut', 'date_fin', 'statut', 'montant_total', 'date_creation')
    list_filter = ('statut', 'date_creation', 'logement', 'client')
    search_fields = ('id__startswith', 'logement__titre', 'client__email', 'client__nom')
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
    # Add Paiement details inline if useful
    # inlines = [PaiementInline] # Assuming PaiementInline is defined in payment/admin.py
    readonly_fields = ('date_creation',)
    fieldsets = (
        ('Reservation Info', {'fields': ('logement', 'client', 'date_debut', 'date_fin')}),
        ('Financials', {'fields': ('montant_total', 'acompte')}),
        ('Status & Dates', {'fields': ('statut', 'date_creation')}),
        # Add paiement field if OneToOne is shown here instead of inline
        # ('Payment', {'fields': ('paiement',)}) # If not using inline
    )
