from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from apps.genealogy.models import Personne
from apps.gallery.models import Media


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class PersonneUpdateForm(forms.ModelForm):
    class Meta:
        model = Personne
        fields = '__all__'
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_deces': forms.DateInput(attrs={'type': 'date'}),
            'biographie': forms.Textarea(attrs={'rows': 3}),
            'signes_distinctifs': forms.Textarea(attrs={'rows': 2}),
        }


class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['fichier', 'type_media', 'titre', 'date_prise_vue', 'est_prive']
        widgets = {
            'date_prise_vue': forms.DateInput(attrs={'type': 'date'}),
        }