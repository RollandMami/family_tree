from django.db import models
from apps.genealogy.models import Personne

class Media(models.Model):
    TYPE_CHOICES = [
        ('IMAGE', 'Image / Photo'),
        ('VIDEO', 'Vidéo'),
    ]

    personne = models.ForeignKey(
        Personne, 
        on_delete=models.CASCADE, 
        related_name='galerie'
    )
    
    titre = models.CharField(max_length=200, blank=True, verbose_name="Légende")
    type_media = models.CharField(max_length=10, choices=TYPE_CHOICES, default='IMAGE')
    fichier = models.FileField(upload_to='gallery/%Y/%m/') # Organisé par date d'upload
    date_prise_vue = models.DateField(null=True, blank=True, help_text="Quand cette photo/vidéo a-t-il été prise ?")
    est_prive = models.BooleanField(default=False, help_text="Cocher pour que seul le cercle proche puisse voir.")
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Média"
        verbose_name_plural = "Galerie Multimédia"
        ordering = ['-date_prise_vue', '-date_ajout']

    def __str__(self):
        return f"{self.type_media} de {self.personne} - {self.titre or 'Sans titre'}"