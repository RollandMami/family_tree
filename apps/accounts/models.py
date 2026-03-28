from django.db import models
from django.contrib.auth.models import User
from apps.genealogy.models import Personne

class Profile(models.Model):
    # Liaison directe avec le compte utilisateur
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Liaison avec la fiche de l'arbre généalogique
    personne = models.OneToOneField(
        Personne, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='compte_utilisateur',
        help_text="Liez cet utilisateur à sa fiche dans l'arbre généalogique."
    )

    def __str__(self):
        return f"Profil de {self.user.username}"