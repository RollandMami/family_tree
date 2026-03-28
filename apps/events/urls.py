from django.urls import path
from .views import creer_evenement, commenter_evenement, reacter_evenement, supprimer_evenement, modifier_evenement, modifier_commentaire

urlpatterns = [
    path('creer/', creer_evenement, name='creer_evenement'),
    path('commenter/<int:event_id>/', commenter_evenement, name='commenter_evenement'),
    path('reacter/<int:event_id>/', reacter_evenement, name='reacter_evenement'),
    path('supprimer/<int:event_id>/', supprimer_evenement, name='supprimer_evenement'),
    path('modifier/<int:event_id>/', modifier_evenement, name='modifier_evenement'),
    path('commentaire/modifier/<int:comment_id>/', modifier_commentaire, name='modifier_commentaire'),
]