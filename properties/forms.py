from django import forms
from .models import Logement

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