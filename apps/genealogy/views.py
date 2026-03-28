from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.events.models import EvenementFamilial
from apps.notifications.models import Notification
from apps.events.utils import obtenir_agenda_proche
from apps.events.forms import EvenementForm
from .models import Personne
from django.shortcuts import get_object_or_404

@login_required
def home(request):
    # 1. Récupérer les événements récents (le "Feed")
    # On prend les 10 derniers événements publiés
    feed_events = EvenementFamilial.objects.all().order_by('-date_evenement')[:10]
    form_event = EvenementForm()

    # 2. Récupérer les alertes J-5 (Anniversaires/Décès)
    agenda = obtenir_agenda_proche(jours=5)

    # 3. Récupérer les notifications non lues de l'utilisateur
    notifications_recentes = Notification.objects.filter(
        destinataire=request.user, 
        est_lue=False
    ).order_by('-date_creation')[:5]

    context = {
        'form_event': form_event,
        'feed_events': feed_events,
        'anniversaires': agenda['anniversaires'],
        'commemorations': agenda['commemorations'],
        'notifications': notifications_recentes,
    }
    
    return render(request, 'genealogy/home.html', context)

@login_required
def person_details(request, person_id):
    personne = get_object_or_404(Personne, id=person_id)
    return render(request, 'genealogy/partials/person_aside.html', {'personne': personne})

@login_required
def person_details_ajax(request, person_id):
    # On récupère la personne ou on renvoie une erreur 404 si elle n'existe pas
    personne = get_object_or_404(Personne, id=person_id)
    
    # On utilise un template spécifique pour le contenu de l'Aside
    return render(request, 'genealogy/partials/person_aside_content.html', {
        'personne': personne
    })

@login_required
def tree_view(request):
    membres = Personne.objects.all()
    
    # On utilise pere_bio__isnull car c'est le nom dans ton modèle
    racines = Personne.objects.filter(
        pere_bio__isnull=True, 
        mere_bio__isnull=True,
        pere_adoptif__isnull=True,
        mere_adoptif__isnull=True
    )
    
    context = {
        'membres': membres,
        'racines': racines,
    }
    return render(request, 'genealogy/tree.html', context)