from django.contrib import admin
from .models import Personne, Couple

class CoupleInline(admin.TabularInline):
    """Permet de voir les mariages directement dans la fiche d'une personne"""
    model = Couple
    fk_name = "homme" # Ou "femme", Django gérera l'affichage
    extra = 1

@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('prenom', 'nom', 'surnom', 'genre', 'est_en_vie', 'localisation_actuelle')
    
    # Filtres sur le côté
    list_filter = ('genre', 'est_en_vie', 'profession')
    
    # Barre de recherche (très utile pour les grands arbres)
    search_fields = ('nom', 'prenom', 'surnom', 'signes_distinctifs')
    
    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        ('Identité', {
            'fields': ('nom', 'prenom', 'surnom', 'genre', 'photo_profil')
        }),
        ('Statut Vital', {
            'fields': ('est_en_vie', 'date_naissance', 'date_deces', 'cause_deces')
        }),
        ('Parenté Biologique', {
            'fields': ('pere_bio', 'mere_bio'),
            'description': "Sélectionnez les parents déjà enregistrés dans la base."
        }),
        ('Parenté Adoptive', {
            'fields': ('pere_adoptif', 'mere_adoptif'),
            'classes': ('collapse',), # Cache cette section par défaut
        }),
        ('Détails & Médias', {
            'fields': ('signes_distinctifs', 'biographie', 'cv_pdf', 'video_presentation')
        }),
        ('Contact & Social', {
            'fields': ('email', 'telephone', 'facebook_url', 'profession', 'etudes', 'localisation_actuelle')
        }),
    )
    inlines = [CoupleInline]

@admin.register(Couple)
class CoupleAdmin(admin.ModelAdmin):
    list_display = ('homme', 'femme', 'statut', 'date_union')
    list_filter = ('statut',)