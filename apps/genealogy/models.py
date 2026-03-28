from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from apps.notifications.models import Notification

class Personne(models.Model):
    GENRE_CHOICES = [('H', 'Homme'), ('F', 'Femme')]

    # --- Informations de base ---
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    surnom = models.CharField(max_length=100, blank=True)
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES)
    
    # --- Statut Vie / Mort ---
    est_en_vie = models.BooleanField(default=True, verbose_name="Est en vie ?")
    date_naissance = models.DateField(null=True, blank=True)
    date_deces = models.DateField(null=True, blank=True, help_text="Laisser vide si en vie")
    cause_deces = models.CharField(max_length=255, blank=True)

    # --- Signes distinctifs & Bio ---
    # On utilise un TextField pour lister plusieurs signes (ex: Chauve, Borgne)
    signes_distinctifs = models.TextField(blank=True, help_text="Ex: Cicatrice joue droite, chauve, etc.")
    biographie = models.TextField(blank=True)
    
    # --- Données Particulières ---
    photo_profil = models.ImageField(upload_to='photos/profils/', blank=True)
    cv_pdf = models.FileField(upload_to='cv/', blank=True)
    video_presentation = models.FileField(upload_to='videos/', blank=True)

    # --- Contact & Social ---
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    facebook_url = models.URLField(blank=True)
    profession = models.CharField(max_length=100, blank=True)
    etudes = models.CharField(max_length=200, blank=True)
    localisation_actuelle = models.CharField(max_length=200, blank=True)

    # --- Parenté Récursive (Le Graphe) ---
    # Parents Biologiques
    pere_bio = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='enfants_bio_pere', limit_choices_to={'genre': 'H'})
    mere_bio = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='enfants_bio_mere', limit_choices_to={'genre': 'F'})
    
    # Parents Adoptifs (Optionnels)
    pere_adoptif = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='enfants_adopt_pere')
    mere_adoptif = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='enfants_adopt_mere')

    # --- Logique métier (Méthodes) ---

    def clean(self):
        """Validation pour empêcher des erreurs de dates logiques"""
        if not self.est_en_vie and not self.date_deces:
            raise ValidationError(_("Si la personne n'est plus en vie, merci d'indiquer la date de décès."))
        if self.date_naissance and self.date_deces and self.date_deces < self.date_naissance:
            raise ValidationError(_("La date de décès ne peut pas être antérieure à la naissance."))

    def get_freres_soeurs_purs(self):
        """Même père ET même mère biologique"""
        if not self.pere_bio or not self.mere_bio:
            return Personne.objects.none()
        return Personne.objects.filter(
            pere_bio=self.pere_bio, 
            mere_bio=self.mere_bio
        ).exclude(id=self.id)

    def get_demi_freres_soeurs(self):
        """Même père OU même mère, mais pas les deux"""
        if not self.pere_bio and not self.mere_bio:
            return Personne.objects.none()
        
        # Enfants ayant le même père mais mère différente
        meme_pere = Personne.objects.filter(pere_bio=self.pere_bio).exclude(mere_bio=self.mere_bio)
        # Enfants ayant la même mère mais père différent
        meme_mere = Personne.objects.filter(mere_bio=self.mere_bio).exclude(pere_bio=self.pere_bio)
        
        return (meme_pere | meme_mere).distinct().exclude(id=self.id)

    def get_relation_to(self, autre):
        """Retourne un libellé de relation proche (frere, cousin, niece_neveu, distant)."""
        if not autre or not isinstance(autre, Personne):
            return 'distant'

        if self.id == autre.id:
            return 'moimeme'

        # Frère/Soeur (pur ou demi)
        if autre in self.get_freres_soeurs_purs() or autre in self.get_demi_freres_soeurs():
            return 'frere'

        # Cousin : parent de l'un est frère/soeur du parent de l'autre
        self_parents = [p for p in (self.pere_bio, self.mere_bio) if p]
        autre_parents = [p for p in (autre.pere_bio, autre.mere_bio) if p]

        for p_self in self_parents:
            for p_autre in autre_parents:
                if p_autre in p_self.get_freres_soeurs_purs() or p_autre in p_self.get_demi_freres_soeurs():
                    return 'cousin'

        # Nièce/Népveu : autre est enfant d'un de mes frères/soeurs
        freres = self.get_freres_soeurs_purs()
        demi = self.get_demi_freres_soeurs()
        siblings_ids = set(freres.values_list('id', flat=True)) | set(demi.values_list('id', flat=True))

        if siblings_ids:
            nieces_neveux = Personne.objects.filter(
                Q(pere_bio__id__in=siblings_ids) | Q(mere_bio__id__in=siblings_ids)
            )
            if nieces_neveux.filter(id=autre.id).exists():
                return 'niece_neveu'

        # Accès minimal pour toute autre branche
        return 'distant'

    @property
    def enfants_bio(self):
        """Retourne tous les enfants biologiques, via père ou mère."""
        return Personne.objects.filter(
            Q(pere_bio=self) | Q(mere_bio=self)
        ).distinct()

    @property
    def photo_profil_url(self):
        """URL de l'image de profil, ou None si non existante."""
        if not self.photo_profil:
            return None
        # Vérifie l'existence du fichier pour éviter les 404
        if self.photo_profil.storage.exists(self.photo_profil.name):
            return self.photo_profil.url
        return None

    def _create_notification_for_all(self, titre, message, type_notif='SYSTEME', lien_url=''):
        for user in User.objects.all():
            Notification.objects.create(
                destinataire=user,
                titre=titre,
                message=message,
                type_notif=type_notif,
                lien_url=lien_url,
            )

    def save(self, *args, **kwargs):
        est_nouvelle = self.pk is None
        ancien_est_en_vie = None

        if not est_nouvelle:
            ancien = Personne.objects.filter(pk=self.pk).first()
            if ancien:
                ancien_est_en_vie = ancien.est_en_vie

        super().save(*args, **kwargs)

        if est_nouvelle:
            self._create_notification_for_all(
                titre=f"Nouvelle personne ajoutée: {self.prenom} {self.nom}",
                message=f"{self.prenom} {self.nom} a été ajouté(e) à la famille.",
                type_notif='SYSTEME',
            )

        if ancien_est_en_vie is True and self.est_en_vie is False:
            self._create_notification_for_all(
                titre=f"Mise à jour : {self.prenom} {self.nom} est décédé(e)",
                message=f"{self.prenom} {self.nom} est passé(e) au statut décédé.",
                type_notif='DECES',
            )

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.surnom})" if self.surnom else f"{self.prenom} {self.nom}"
    

class Couple(models.Model):
    STATUT_UNION = [
        ('EN_COUPLE', 'En couple'),
        ('FIANCE', 'Fiancés'),
        ('MARIE', 'Mariés'),
        ('DIVORCE', 'Divorcés'),
        ('VEUF', 'Veuf/Veuve'),
    ]

    homme = models.ForeignKey(Personne, on_delete=models.CASCADE, related_name='unions_h', limit_choices_to={'genre': 'H'})
    femme = models.ForeignKey(Personne, on_delete=models.CASCADE, related_name='unions_f', limit_choices_to={'genre': 'F'})
    
    statut = models.CharField(max_length=20, choices=STATUT_UNION, default='EN_COUPLE')
    date_union = models.DateField(null=True, blank=True)
    date_separation = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Union: {self.homme.prenom} & {self.femme.prenom} - {self.get_statut_display()}"