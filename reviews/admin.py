from django.contrib import admin
from .models import Commentaire

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('logement', 'auteur', 'note', 'date_publication', 'valide_par_admin')
    list_filter = ('valide_par_admin', 'note', 'date_publication', 'logement')
    search_fields = ('texte', 'auteur__email', 'logement__titre')
    date_hierarchy = 'date_publication'
    ordering = ('-date_publication',)
    readonly_fields = ('date_publication',)
    raw_id_fields = ('logement', 'auteur') # Use search popup for foreign keys
    actions = ['approve_comments']

    fieldsets = (
        (None, {'fields': ('logement', 'auteur')}),
        ('Review Details', {'fields': ('note', 'texte', 'valide_par_admin')}),
        ('Date', {'fields': ('date_publication',)}),
    )

    def approve_comments(self, request, queryset):
        queryset.update(valide_par_admin=True)
    approve_comments.short_description = "Approuver les commentaires sélectionnés"
