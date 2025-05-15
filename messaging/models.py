import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from properties.models import Logement

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Link message to a specific logement conversation thread
    logement = models.ForeignKey(
        Logement,
        verbose_name=_('logement concerné'),
        on_delete=models.CASCADE,
        related_name='messages',
        null=True, # Allow messages not directly linked to one logement?
        blank=True
    )
    emetteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('émetteur'),
        on_delete=models.CASCADE, # Or SET_NULL if message should persist after user deletion
        related_name='messages_envoyes'
    )
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('destinataire'),
        on_delete=models.CASCADE, # Or SET_NULL
        related_name='messages_recus'
    )
    contenu = models.TextField(_('contenu'))
    date_envoi = models.DateTimeField(_('date d\'envoi'), default=timezone.now)
    lu = models.BooleanField(_('lu'), default=False)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['-date_envoi']

    def __str__(self):
        return f"Message de {self.emetteur} à {self.destinataire} ({self.date_envoi:%Y-%m-%d %H:%M})"
