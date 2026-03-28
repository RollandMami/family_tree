from django.urls import path
from .views import creer_evenement

urlpatterns = [
    path('creer/', creer_evenement, name='creer_evenement'),
]