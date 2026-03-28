from django import forms
from .models import Personne


class AddMemberForm(forms.ModelForm):
    relation_type = forms.ChoiceField(choices=[('enfant', 'Enfant'), ('conjoint', 'Conjoint')], widget=forms.HiddenInput)
    related_person_id = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Personne
        fields = ['prenom', 'nom', 'genre', 'date_naissance', 'est_en_vie', 'date_deces']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_deces': forms.DateInput(attrs={'type': 'date'}),
            'est_en_vie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'genre': forms.Select(choices=Personne.GENRE_CHOICES, attrs={'class': 'form-select form-select-sm'}),
        }
        labels = {
            'date_deces': 'Date de décès',
            'prenom': 'Prénom',
            'nom': 'Nom',
            'genre': 'Genre',
            'date_naissance': 'Date de naissance',
            'est_en_vie': 'Est en vie',
        }
