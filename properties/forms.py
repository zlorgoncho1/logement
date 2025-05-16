from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from .models import Logement, Disponibilite
# Assuming Fichier model is in fichiers.models, it will be handled in the view, not directly in this form for M2M.

# Tailwind classes (assuming they are defined or this is a common pattern)
TAILWIND_INPUT_CLASSES = (
    "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
    "placeholder-gray-400 focus:outline-none focus:ring-indigo-500 "
    "focus:border-indigo-500 sm:text-sm"
)
TAILWIND_TEXTAREA_CLASSES = TAILWIND_INPUT_CLASSES # Often the same
TAILWIND_SELECT_CLASSES = TAILWIND_INPUT_CLASSES # Often the same
TAILWIND_FILE_INPUT_CLASSES = (
    "mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer "
    "bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
)
TAILWIND_DATE_INPUT_CLASSES = TAILWIND_INPUT_CLASSES

class PropertyForm(forms.ModelForm):
    photos_upload = forms.FileField(
        label=_("Photos du logement"),
        widget=forms.TextInput(attrs={
            "name": "images",
            "type": "File",
            "class": "form-control",
            "multiple": "True",
        }),
        required=False, # Allow creating property without photos initially, or make True if mandatory
        help_text=_("Vous pouvez sélectionner plusieurs images.")
    )

    class Meta:
        model = Logement
        fields = [
            'titre', 'type', 'adresse', 'description', 
            'prix_par_nuit', 'equipements'
        ]
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': _('Ex: Villa spacieuse avec piscine'), 'class': TAILWIND_INPUT_CLASSES}),
            'type': forms.Select(attrs={'class': TAILWIND_SELECT_CLASSES}),
            'adresse': forms.TextInput(attrs={'placeholder': _('Ex: 123, Rue de la Paix, Dakar'), 'class': TAILWIND_INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Décrivez en détail votre logement...'), 'class': TAILWIND_TEXTAREA_CLASSES}),
            'prix_par_nuit': forms.NumberInput(attrs={'placeholder': _('Prix en FCFA'), 'class': TAILWIND_INPUT_CLASSES}),
            'equipements': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Ex: Wifi, Cuisine équipée, Climatisation, TV'), 'class': TAILWIND_TEXTAREA_CLASSES, 'help_text': _('Liste des équipements séparés par des virgules.')}),
        }
        labels = {
            'titre': _("Titre de l'annonce"),
            'type': _("Type de logement"),
            'adresse': _("Adresse complète"),
            'description': _("Description détaillée"),
            'prix_par_nuit': _("Prix par nuit (FCFA)"),
            'equipements': _("Équipements (séparés par des virgules)"),
        }

# Using DateInput for date fields, you might want to use a JavaScript date picker widget in the template for better UX.
AvailabilityFormSet = inlineformset_factory(
    Logement, 
    Disponibilite, 
    fields=('date_debut', 'date_fin', 'est_disponible'),
    extra=2, # Number of empty forms to display
    can_delete=True, # Allow deletion of existing availability entries
    min_num=1, # Minimum number of forms to display
    max_num=10, # Maximum number of forms to display
    widgets={
        'date_debut': forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_DATE_INPUT_CLASSES}),
        'date_fin': forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_DATE_INPUT_CLASSES}),
        'est_disponible': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}), # Example Tailwind for checkbox
    },
    labels={
        'date_debut': _("Date de début"),
        'date_fin': _("Date de fin"),
        'est_disponible': _("Est disponible?"),
    }
)

class PropertySearchForm(forms.Form):
    location = forms.CharField(
        max_length=100,
        required=False,
        label='Lieu',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Entrez une ville ou un quartier'
        })
    )
    property_type = forms.ChoiceField(
        choices=[('', 'Tous')] + Logement.LogementType.choices,
        required=False,
        label='Type de logement',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    min_price = forms.DecimalField(
        required=False,
        label='Prix Min',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Prix minimum'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        label='Prix Max',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Prix maximum'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")

        if min_price is not None and max_price is not None and min_price > max_price:
            raise forms.ValidationError("Le prix minimum ne peut pas être supérieur au prix maximum.")
        return cleaned_data