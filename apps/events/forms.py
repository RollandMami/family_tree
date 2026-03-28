from django import forms
from .models import EvenementFamilial

class EvenementForm(forms.ModelForm):
    class Meta:
        model = EvenementFamilial
        fields = ['titre', 'type_evt', 'date_evenement', 'lieu', 'description', 'participants']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Baptême de mon fils'}),
            'type_evt': forms.Select(attrs={'class': 'form-select'}),
            'date_evenement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu de l\'événement'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }