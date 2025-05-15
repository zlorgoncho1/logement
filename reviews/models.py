from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from properties.models import Logement

# Create your models here.

class Commentaire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logement = models.ForeignKey(
        Logement,
        verbose_name=_('logement évalué'),
        on_delete=models.CASCADE,
        related_name='commentaires'
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('auteur'),
        on_delete=models.CASCADE, # Or SET_NULL if comments should persist
        related_name='commentaires_laisses',
        limit_choices_to={'type': 'CLIENT'} # Only Clients can leave reviews
    )
    note = models.IntegerField(
        _('note (1 à 5)'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    texte = models.TextField(_('texte du commentaire'))
    date_publication = models.DateTimeField(_('date de publication'), default=timezone.now)
    valide_par_admin = models.BooleanField(_('validé par admin'), default=False) # For moderation

    class Meta:
        verbose_name = _('Commentaire')
        verbose_name_plural = _('Commentaires')
        ordering = ['-date_publication']
        # Prevent a user from reviewing the same logement multiple times?
        # unique_together = (('logement', 'auteur'),) # If so

    def __str__(self):
        return f"Commentaire de {self.auteur.email} sur {self.logement.titre} - Note: {self.note}/5"
