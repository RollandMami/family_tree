from django.db import models
from apps.genealogy.models import Personne
from django.contrib.auth.models import User
from apps.notifications.models import Notification

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
    image = models.ImageField(upload_to='events/images/', blank=True, null=True)
    
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


class Commentaire(models.Model):
    evenement = models.ForeignKey(EvenementFamilial, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentaires')
    texte = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        est_nouveau = self.pk is None
        super().save(*args, **kwargs)
        if est_nouveau and self.evenement.organisateur and self.evenement.organisateur != self.auteur:
            Notification.objects.create(
                destinataire=self.evenement.organisateur,
                titre=f"Commentaire sur votre publication: {self.evenement.titre}",
                message=f"{self.auteur.username} a commenté : {self.texte[:100]}",
                type_notif='COMMENTAIRE',
                lien_url='/'
            )

    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur {self.evenement.titre}"


class Reaction(models.Model):
    TYPES = [
        ('LIKE', 'J’aime'),
        ('LOVE', 'J’adore'),
        ('WOW', 'Wahoo'),
        ('SAD', 'Triste'),
        ('ANGRY', 'En colère'),
    ]

    evenement = models.ForeignKey(EvenementFamilial, on_delete=models.CASCADE, related_name='reactions')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    type_reaction = models.CharField(max_length=10, choices=TYPES)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('evenement', 'utilisateur', 'type_reaction')

    def save(self, *args, **kwargs):
        est_nouveau = self.pk is None
        super().save(*args, **kwargs)
        if est_nouveau and self.evenement.organisateur and self.evenement.organisateur != self.utilisateur:
            Notification.objects.create(
                destinataire=self.evenement.organisateur,
                titre=f"Réaction sur votre publication: {self.evenement.titre}",
                message=f"{self.utilisateur.username} a réagi ({self.get_type_reaction_display()}).",
                type_notif='REACTION',
                lien_url='/'
            )

    def __str__(self):
        return f"{self.utilisateur.username} a réagi {self.get_type_reaction_display()}"