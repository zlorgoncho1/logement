from django.contrib import admin
from .models import Paiement

# Could be used as an inline in ReservationAdmin
# class PaiementInline(admin.StackedInline): # Or TabularInline
#    model = Paiement
#    can_delete = False # Usually don't delete payment from reservation view
#    verbose_name_plural = 'Paiement'
#    fk_name = 'reservation'
#    extra = 0 # Don't show extra forms

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'montant', 'methode', 'statut', 'date_paiement')
    list_filter = ('statut', 'methode', 'date_paiement')
    search_fields = ('id__startswith', 'reservation__id__startswith', 'transaction_id', 'reservation__client__email')
    date_hierarchy = 'date_paiement'
    ordering = ('-date_paiement',)
    readonly_fields = ('date_paiement',) # Usually set automatically
    # Make reservation field read-only or searchable
    raw_id_fields = ('reservation',)
    fieldsets = (
        (None, {'fields': ('reservation',)}),
        ('Payment Details', {'fields': ('montant', 'methode', 'statut', 'transaction_id')}),
        ('Date', {'fields': ('date_paiement',)}),
    )
