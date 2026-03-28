from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('ANNIVERSAIRE', 'Anniversaire de naissance'),
        ('DECES', 'Commémoration de décès'),
        ('EVENEMENT', 'Événement familial'),
        ('SYSTEME', 'Message système'),
    ]

    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=255)
    message = models.TextField()
    type_notif = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    est_lue = models.BooleanField(default=False)
    
    # Optionnel : lien vers l'objet qui a généré la notif (ex: ID de la personne)
    lien_url = models.CharField(max_length=255, blank=True, help_text="Lien vers la fiche concernée")

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Notif pour {self.destinataire.username} : {self.titre}"