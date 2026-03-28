from django.urls import path
from .views import register # Assure-toi que la vue 'register' existe dans views.py

urlpatterns = [
    path('register/', register, name='register'),
]