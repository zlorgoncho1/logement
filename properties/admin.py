from django.contrib import admin
from .models import Logement, Disponibilite

class DisponibiliteInline(admin.TabularInline):
    model = Disponibilite
    extra = 1 # Number of empty forms to display
    fields = ('date_debut', 'date_fin', 'est_disponible')

@admin.register(Logement)
class LogementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'agent', 'type', 'prix_par_nuit', 'statut', 'date_creation')
    list_filter = ('type', 'statut', 'agent')
    search_fields = ('titre', 'adresse', 'description', 'agent__email')
    ordering = ('-date_creation',)
    # Use filter_horizontal for ManyToMany fields if they get large
    filter_horizontal = ('photos',)
    # Add inlines for related models
    inlines = [DisponibiliteInline]
    # Customize fieldsets for better layout
    fieldsets = (
        (None, {'fields': ('titre', 'agent', 'type', 'adresse')}),
        ('Details', {'fields': ('description', 'prix_par_nuit', 'equipements')}),
        ('Media', {'fields': ('photos',)}),
        ('Status & Dates', {'fields': ('statut', 'date_creation', 'date_modification')}),
    )
    readonly_fields = ('date_creation', 'date_modification')

@admin.register(Disponibilite)
class DisponibiliteAdmin(admin.ModelAdmin):
    list_display = ('logement', 'date_debut', 'date_fin', 'est_disponible')
    list_filter = ('est_disponible', 'logement')
    search_fields = ('logement__titre',)
    date_hierarchy = 'date_debut'
    ordering = ('logement', 'date_debut')
