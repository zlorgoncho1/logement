from django.contrib import admin
from django.http import FileResponse, HttpResponseRedirect
from .models import Fichier
from django.utils.html import mark_safe
from django.contrib import messages

@admin.action(description='Télécharger le fichier')
def download_fichier(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.error(request, 'Veuillez sélectionner un seul fichier')
        return

    fichier = queryset.first()
    response = FileResponse(fichier.fichier, as_attachment=True, filename=fichier.fichier.name)
    return response

@admin.register(Fichier)
class FichierAdmin(admin.ModelAdmin):
    list_display = ('nom_fichier', 'type', 'date_upload', 'url')
    search_fields = ('nom_fichier', 'type')
    list_filter = ('type', 'date_upload')
    readonly_fields = ('url',)
    actions = [download_fichier]

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('fichier',)
        return self.readonly_fields 