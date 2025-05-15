import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from bookings.models import Reservation

class Paiement(models.Model):
    class MethodePaiement(models.TextChoices):
        MOBILE_MONEY = 'MMONEY', _('Mobile Money')
        CARTE = 'CARTE', _('Carte Bancaire')
        ESPECES = 'ESPECES', _('Espèces')
        # Add specific Mobile Money operators if needed, e.g., ORANGE_MONEY, WAVE

    class StatutPaiement(models.TextChoices):
        EN_ATTENTE = 'ATTENTE', _('En attente')
        REUSSI = 'REUSSI', _('Réussi')
        ECHOUE = 'ECHOUE', _('Échoué')
        REMBOURSE = 'REMBOURSE', _('Remboursé')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.OneToOneField(
        Reservation,
        verbose_name=_('réservation'),
        on_delete=models.CASCADE, # If reservation is deleted, payment is too.
        related_name='paiement'
    )
    methode = models.CharField(
        _('méthode de paiement'),
        max_length=10,
        choices=MethodePaiement.choices,
        default=MethodePaiement.MOBILE_MONEY
    )
    statut = models.CharField(
        _('statut du paiement'),
        max_length=10,
        choices=StatutPaiement.choices,
        default=StatutPaiement.EN_ATTENTE
    )
    montant = models.DecimalField(
        _('montant payé'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    date_paiement = models.DateTimeField(_('date de paiement'), default=timezone.now)
    transaction_id = models.CharField(_('ID de transaction externe'), max_length=255, blank=True, null=True) # For external payment gateways

    class Meta:
        verbose_name = _('Paiement')
        verbose_name_plural = _('Paiements')
        ordering = ['-date_paiement']

    def __str__(self):
        return f"Paiement {self.id} pour Réservation {self.reservation.id} - {self.get_statut_display()}"
