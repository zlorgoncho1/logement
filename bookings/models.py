from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from accounts.models import Client
from properties.models import Logement

# Create your models here.

class Reservation(models.Model):
    class StatutReservation(models.TextChoices):
        EN_ATTENTE = 'ATTENTE', _('En attente')
        CONFIRMEE = 'CONFIRMEE', _('Confirmée')
        ANNULEE = 'ANNULEE', _('Annulée')
        TERMINEE = 'TERMINEE', _('Terminée')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        Client,
        verbose_name=_('client'),
        on_delete=models.CASCADE,
        related_name='reservations',
    )
    logement = models.ForeignKey(
        Logement,
        verbose_name=_('logement'),
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    date_debut = models.DateField(_('date de début'))
    date_fin = models.DateField(_('date de fin'))
    statut = models.CharField(
        _('statut'),
        max_length=10,
        choices=StatutReservation.choices,
        default=StatutReservation.EN_ATTENTE
    )
    montant_total = models.DecimalField(
        _('montant total'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    acompte = models.DecimalField(
        _('acompte versé'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    date_creation = models.DateTimeField(_('date de création'), default=timezone.now)

    class Meta:
        verbose_name = _('Réservation')
        verbose_name_plural = _('Réservations')
        ordering = ['-date_creation']
        constraints = [
            models.CheckConstraint(check=models.Q(date_fin__gte=models.F('date_debut')),
                                   name='booking_date_fin_gte_date_debut'),
            # Add constraint to prevent overlapping reservations for the same logement?
            # This requires more complex logic, potentially at the view/form level or using database functions.
        ]

    def __str__(self):
        return f"Réservation {self.id} pour {self.logement.titre} par {self.client.email}"
