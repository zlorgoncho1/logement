from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm # Import AuthenticationForm
from .models import CustomUser
from django.core.exceptions import ValidationError

# Common Tailwind classes for form inputs
TAILWIND_INPUT_CLASSES = (
    "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
    "placeholder-gray-400 focus:outline-none focus:ring-indigo-500 "
    "focus:border-indigo-500 sm:text-sm"
)

TAILWIND_PASSWORD_INPUT_CLASSES = TAILWIND_INPUT_CLASSES
TAILWIND_FILE_INPUT_CLASSES = (
    "mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer "
    "bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
) # Basic styling for file input

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField( # Changed from CharField to EmailField for clarity
        label=_("Adresse Email"),
        widget=forms.EmailInput(attrs={
            'autofocus': True, 
            'placeholder': _('votreadresse@email.com'),
            'class': TAILWIND_INPUT_CLASSES
        })
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': _('Votre mot de passe'),
            'class': TAILWIND_PASSWORD_INPUT_CLASSES
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        # Since CustomUser uses 'email' as USERNAME_FIELD, 
        # AuthenticationForm's 'username' field should be treated as email.
        self.fields['username'].label = _("Adresse Email")
        self.fields['username'].widget.attrs['placeholder'] = _('votreadresse@email.com')


class ClientRegistrationStartForm(forms.Form):
    email_or_phone = forms.CharField(
        label=_("Email ou Numéro de téléphone"),
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': _('Saisissez votre email ou téléphone'),
            'class': TAILWIND_INPUT_CLASSES
        })
    )
    # In a real scenario, you'd validate if it's a valid email or phone format
    # and potentially check for uniqueness if starting with unique identifier.

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        label=_("Code OTP"),
        max_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': _('Saisissez le code à 6 chiffres'),
            'class': TAILWIND_INPUT_CLASSES
        })
    )

class ClientProfileCompletionForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Créez un mot de passe sécurisé'),
            'class': TAILWIND_PASSWORD_INPUT_CLASSES
        }), 
        label=_("Mot de passe")
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Confirmez votre mot de passe'),
            'class': TAILWIND_PASSWORD_INPUT_CLASSES
        }), 
        label=_("Confirmez le mot de passe")
    )
    
    # Add email field explicitly if it might not be set by USERNAME_FIELD handling
    # and if registration can start with phone only.
    email = forms.EmailField(
        label=_("Adresse Email"), 
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': _('Votre adresse email'),
            'class': TAILWIND_INPUT_CLASSES
        })
    )
    telephone = forms.CharField(
        label=_("Numéro de téléphone"), 
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Votre numéro de téléphone (optionnel)'),
            'class': TAILWIND_INPUT_CLASSES
        })
    )

    class Meta:
        model = CustomUser
        fields = ['nom', 'prenom', 'email', 'telephone', 'password'] # 'email' is USERNAME_FIELD
        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': _('Votre nom de famille'),
                'class': TAILWIND_INPUT_CLASSES
            }),
            'prenom': forms.TextInput(attrs={
                'placeholder': _('Votre prénom'),
                'class': TAILWIND_INPUT_CLASSES
            }),
            'email': forms.EmailInput(attrs={'placeholder': _('Votre adresse email')}),
            'telephone': forms.TextInput(attrs={'placeholder': _('Votre numéro de téléphone (optionnel)')}),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))
        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get('email').lower() # Normalize email to lowercase
        if CustomUser.objects.filter(email=email).exists():
            # If it's an update form, you might want to exclude the current instance
            # if self.instance and self.instance.pk and self.instance.email == email:
            #     pass # Allow current email
            # else:
            raise forms.ValidationError(_("Un compte avec cet email existe déjà."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower() # Ensure email is saved in lowercase
        user.set_password(self.cleaned_data["password"])
        user.type = CustomUser.UserType.CLIENT # Set user type
        if commit:
            user.save()
        return user 

class AgentRegistrationForm(forms.Form):
    nom = forms.CharField(
        label=_("Nom de famille"),
        max_length=150, 
        widget=forms.TextInput(attrs={
            'placeholder': _('Votre nom de famille'),
            'class': TAILWIND_INPUT_CLASSES
        })
    )
    prenom = forms.CharField(
        label=_("Prénom"),
        max_length=150, 
        widget=forms.TextInput(attrs={
            'placeholder': _('Votre prénom'),
            'class': TAILWIND_INPUT_CLASSES
        })
    )
    email = forms.EmailField(
        label=_("Adresse Email"),
        widget=forms.EmailInput(attrs={
            'placeholder': _('votreadresse@email.com'),
            'class': TAILWIND_INPUT_CLASSES
        })
    )
    telephone = forms.CharField(
        label=_("Numéro de téléphone"),
        max_length=20, 
        required=False, # As per CustomUser model, can be True if mandatory for agents
        widget=forms.TextInput(attrs={
            'placeholder': _('Votre numéro de téléphone (optionnel)'),
            'class': TAILWIND_INPUT_CLASSES
        })
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Créez un mot de passe sécurisé'),
            'class': TAILWIND_PASSWORD_INPUT_CLASSES
        })
    )
    password_confirm = forms.CharField(
        label=_("Confirmer le mot de passe"),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Confirmez votre mot de passe'),
            'class': TAILWIND_PASSWORD_INPUT_CLASSES
        })
    )
    document_kyc = forms.FileField(
        label=_("Document KYC (pièce d'identité, etc.)"), 
        required=True, # As per use case scenario
        widget=forms.ClearableFileInput(attrs={
            'class': TAILWIND_FILE_INPUT_CLASSES 
            # Add 'multiple': True here if allowing multiple KYC docs via one field, though view logic handles one file now.
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("Un utilisateur avec cet email existe déjà."))
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError(_("Les mots de passe ne correspondent pas."))
        return password_confirm

    def clean_document_kyc(self):
        document = self.cleaned_data.get('document_kyc')
        if document:
            # Max file size: 5MB
            if document.size > 5 * 1024 * 1024:
                 raise ValidationError(_("Le fichier est trop volumineux. La taille maximale est de 5MB."))
            # Allowed content types (example)
            # valid_mime_types = ['image/jpeg', 'image/png', 'application/pdf']
            # if document.content_type not in valid_mime_types:
            #     raise ValidationError(_("Type de fichier non supporté. Veuillez télécharger une image (JPEG, PNG) ou un PDF."))
        return document 