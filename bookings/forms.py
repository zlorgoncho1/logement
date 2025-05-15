from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

class BookingForm(forms.Form):
    date_arrivee = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded mt-1'}),
        label='Date d\'arrivée'
    )
    date_depart = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded mt-1'}),
        label='Date de départ'
    )

    def clean_date_arrivee(self):
        date_arrivee = self.cleaned_data.get('date_arrivee')
        if date_arrivee and date_arrivee < timezone.now().date():
            raise ValidationError("La date d'arrivée ne peut pas être dans le passé.")
        return date_arrivee

    def clean_date_depart(self):
        date_depart = self.cleaned_data.get('date_depart')
        date_arrivee = self.cleaned_data.get('date_arrivee')
        if date_depart and date_arrivee and date_depart <= date_arrivee:
            raise ValidationError("La date de départ doit être après la date d'arrivée.")
        if date_depart and date_depart < timezone.now().date():
            raise ValidationError("La date de départ ne peut pas être dans le passé.")
        return date_depart 