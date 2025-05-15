import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Fichier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Using FileField, can be changed to ImageField if only images are expected
    fichier = models.FileField(_('fichier'), upload_to='fichiers/%Y/%m/%d/')
    nom_fichier = models.CharField(_('nom du fichier'), max_length=255, blank=True)
    type = models.CharField(_('type MIME'), max_length=100, blank=True) # Store MIME type
    date_upload = models.DateTimeField(_('date d\'upload'), default=timezone.now)

    # Relation added later via ManyToMany fields in Logement and AgentImmobilier
    # logement = models.ForeignKey('properties.Logement', on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    # agent_kyc = models.ForeignKey('accounts.AgentImmobilier', on_delete=models.CASCADE, related_name='documents_kyc', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.nom_fichier:
            self.nom_fichier = self.fichier.name
        # Attempt to get mime type if not provided - might need python-magic library
        # if not self.type and hasattr(self.fichier.file, 'content_type'):
        #    self.type = self.fichier.file.content_type
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom_fichier or str(self.id)

    @property
    def url(self):
        return  self.fichier.url if self.fichier else '' 