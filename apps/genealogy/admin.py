from django.contrib import admin
from .models import Personne, Couple

class MariInline(admin.TabularInline):
    """S'affiche sur la fiche d'une FEMME pour montrer ses MARIS"""
    model = Couple
    fk_name = "femme" # L'ancre est la femme, on affiche donc le champ 'homme'
    verbose_name = "Conjoint (Mari)"
    verbose_name_plural = "Conjoints (Maris)"
    extra = 1
    template = 'admin/edit_inline/tabular.html'

class FemmeInline(admin.TabularInline):
    """S'affiche sur la fiche d'un HOMME pour montrer ses FEMMES"""
    model = Couple
    fk_name = "homme" # L'ancre est l'homme, on affiche donc le champ 'femme'
    verbose_name = "Conjoint (Épouse)"
    verbose_name_plural = "Conjoints (Épouses)"
    extra = 1
    template = 'admin/edit_inline/tabular.html'

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
    
    def get_inline_instances(self, request, obj=None):
        """
        On surcharge cette méthode pour s'assurer que l'inline 
        est proprement instancié avec un préfixe unique.
        """
        inline_instances = []
        inlines = self.get_inlines(request, obj)
        
        for inline_class in inlines:
            # On donne un nom unique selon le genre pour éviter le conflit ManagementForm
            prefix = "unions_h" if inline_class == FemmeInline else "unions_f"
            inline_instances.append(inline_class(self.model, self.admin_site))
            
        return inline_instances
    
    def get_inlines(self, request, obj=None):
        """
        Cette méthode choisit dynamiquement l'inline à afficher 
        selon le genre de la personne consultée.
        """
        if obj:
            if obj.genre == 'H':
                return [FemmeInline]
            elif obj.genre == 'F':
                return [MariInline]
        return []

@admin.register(Couple)
class CoupleAdmin(admin.ModelAdmin):
    list_display = ('homme', 'femme', 'statut', 'date_union')
    list_filter = ('statut',)