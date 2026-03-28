from django.contrib import admin
from .models import Media

class MediaInline(admin.TabularInline):
    model = Media
    extra = 3 # Affiche 3 emplacements vides par défaut
    fields = ('fichier', 'type_media', 'titre', 'date_prise_vue', 'est_prive')

# On va "greffer" cet inline sur l'admin de Personne qui est dans une autre app
from apps.genealogy.admin import PersonneAdmin
from apps.genealogy.models import Personne

# On désenregistre l'ancien et on réenregistre avec la galerie
admin.site.unregister(Personne)

@admin.register(Personne)
class PersonneWithGalleryAdmin(PersonneAdmin):
    # On garde les inlines de couples et on ajoute la galerie
    def get_inlines(self, request, obj=None):
        inlines = super().get_inlines(request, obj)
        return inlines + [MediaInline]