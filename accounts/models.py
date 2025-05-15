import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # Superuser should be active by default
        extra_fields.setdefault('type', CustomUser.UserType.ADMIN) # Set type for superuser

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        CLIENT = 'CLIENT', _('Client')
        AGENT = 'AGENT', _('Agent Immobilier')
        ADMIN = 'ADMIN', _('Administrateur') # Added Admin type

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(_('nom'), max_length=150)
    prenom = models.CharField(_('prénom'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    telephone = models.CharField(_('téléphone'), max_length=20, blank=True, null=True) # Made optional initially
    type = models.CharField(
        _('type'),
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT
    )
    date_creation = models.DateTimeField(_('date de création'), default=timezone.now)
    is_staff = models.BooleanField(default=False) # Required for Django admin
    is_active = models.BooleanField(default=True) # Users active by default, can be deactivated by admin
    is_superuser = models.BooleanField(default=False) # Explicitly add is_superuser

    # Add related_name to avoid clashes with auth.User default
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set",
        related_query_name="user",
    )


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom'] # Email and password are required by default

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.prenom} {self.nom}"

# Proxy models for specific user types
class ClientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=CustomUser.UserType.CLIENT)

class Client(CustomUser):
    objects = ClientManager()
    class Meta:
        proxy = True
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')

class AgentImmobilierManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=CustomUser.UserType.AGENT)

class AgentImmobilier(CustomUser):
    objects = AgentImmobilierManager()
    class Meta:
        proxy = True
        verbose_name = _('Agent Immobilier')
        verbose_name_plural = _('Agents Immobiliers')

    # Add specific agent fields if needed, e.g., documentsKYC
    # documentsKYC = models.ManyToManyField('fichiers.Fichier', blank=True, related_name='kyc_for_agent')

# Consider adding a separate Fichier app/model later if needed
# Or use a JSONField/FileField directly on AgentImmobilier if simple
