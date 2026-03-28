from django.db import models
from apps.genealogy.models import Personne
from django.contrib.auth.models import User

class EvenementFamilial(models.Model):
    TYPE_EVT = [
        ('MARIAGE', 'Mariage'),
        ('BAPTEME', 'Baptême'),
        ('REUNION', 'Réunion de famille'),
        ('GRADUATION', 'Diplôme / Succès'),
        ('FIANCAILLES', 'Vodiondry / soratra'),
        ('FUNEBRE', 'Decès'),
        ('AUTRE', 'Autre'),
    ]

    titre = models.CharField(max_length=200)
    type_evt = models.CharField(max_length=20, choices=TYPE_EVT)
    date_evenement = models.DateField()
    description = models.TextField(blank=True)
    lieu = models.CharField(max_length=255, blank=True)
    
    # Un événement peut concerner plusieurs personnes (ex: deux mariés)
    participants = models.ManyToManyField(Personne, related_name='evenements_lies')

    organisateur = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='evenements_crees'
    )
    
    est_valide = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Événement"
        ordering = ['date_evenement']

    def __str__(self):
        return f"{self.titre} - {self.date_evenement}"