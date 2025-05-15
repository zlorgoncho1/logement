import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

class Logement(models.Model):
    class LogementType(models.TextChoices):
        MAISON = 'MAISON', _('Maison')
        APPARTEMENT = 'APPART', _('Appartement')
        STUDIO = 'STUDIO', _('Studio')
        CHAMBRE = 'CHAMBRE', _('Chambre')

    class StatutLogement(models.TextChoices):
        PUBLIE = 'PUBLIE', _('Publié')
        DESACTIVE = 'DESACTIVE', _('Désactivé')
        EN_ATTENTE = 'ATTENTE', _('En attente de validation')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titre = models.CharField(_('titre'), max_length=255)
    type = models.CharField(
        _('type de logement'),
        max_length=10,
        choices=LogementType.choices,
        default=LogementType.APPARTEMENT
    )
    adresse = models.CharField(_('adresse'), max_length=255)
    description = models.TextField(_('description'))
    prix_par_nuit = models.DecimalField(
        _('prix par nuit'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    # Using TextField for simplicity, consider JSONField or ManyToMany to an Equipement model
    equipements = models.TextField(_('équipements'), blank=True, help_text=_('Liste d\'équipements séparés par des virgules'))
    photos = models.ManyToManyField(
        'fichiers.Fichier', # Use the string format 'app_name.ModelName'
        verbose_name=_('photos'),
        blank=True,
        related_name='logements'
    )
    statut = models.CharField(
        _('statut'),
        max_length=10,
        choices=StatutLogement.choices,
        default=StatutLogement.EN_ATTENTE
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Link to CustomUser
        verbose_name=_('agent immobilier'),
        on_delete=models.CASCADE,
        related_name='logements_proposes',
        limit_choices_to={'type': 'AGENT'} # Ensure only Agents can be selected
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    favorited_by = models.ManyToManyField(
        'accounts.Client',
        related_name='logements_favoris',
        blank=True
    )


    def __str__(self):
        return self.titre

    def get_equipements_list(self):
        return [e.strip() for e in self.equipements.split(',') if e.strip()]

class Disponibilite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logement = models.ForeignKey(
        Logement,
        verbose_name=_('logement'),
        on_delete=models.CASCADE,
        related_name='disponibilites'
    )
    date_debut = models.DateField(_('date de début'))
    date_fin = models.DateField(_('date de fin'))
    est_disponible = models.BooleanField(_('est disponible'), default=True)

    class Meta:
        verbose_name = _('Disponibilité')
        verbose_name_plural = _('Disponibilités')
        ordering = ['date_debut']
        constraints = [
            models.CheckConstraint(check=models.Q(date_fin__gte=models.F('date_debut')),
                                   name='date_fin_gte_date_debut'),
            models.UniqueConstraint(fields=['logement', 'date_debut', 'date_fin'], name='unique_disponibilite_par_logement_et_dates')
        ]

    def __str__(self):
        return f"{self.logement.titre}: {self.date_debut} - {self.date_fin} ({_('Disponible' if self.est_disponible else 'Non disponible')})"

# Add Client favoris relationship here or in accounts/models.py
# # We'll add ManyToManyField `favoris` to `accounts.Client` (or `CustomUser`) later if needed.

# # Add Agent documents KYC relationship here or in accounts/models.py
# # We'll add ManyToManyField `documents_kyc` to `accounts.AgentImmobilier` (or `CustomUser`) later if needed.
