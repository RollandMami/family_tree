from django.urls import path
from .views import creer_evenement, commenter_evenement, reacter_evenement

urlpatterns = [
    path('creer/', creer_evenement, name='creer_evenement'),
    path('commenter/<int:event_id>/', commenter_evenement, name='commenter_evenement'),
    path('reacter/<int:event_id>/', reacter_evenement, name='reacter_evenement'),
]