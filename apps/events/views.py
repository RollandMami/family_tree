from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from apps.notifications.models import Notification
from .forms import EvenementForm
from .models import EvenementFamilial, Commentaire, Reaction

@login_required
def creer_evenement(request):
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            evenement = form.save(commit=False)
            evenement.organisateur = request.user # On lie l'auteur
            evenement.save()
            form.save_m2m() # Important pour les participants (Many-to-Many)

            # Notification pour tous les utilisateurs concernant le nouvel événement
            for user in User.objects.all():
                Notification.objects.create(
                    destinataire=user,
                    titre=f"Nouvel événement : {evenement.titre}",
                    message=f"{request.user.username} a publié l'événement '{evenement.titre}' pour le {evenement.date_evenement}.",
                    type_notif='EVENEMENT',
                    lien_url='/'
                )
    return redirect('home')

@login_required
def commenter_evenement(request, event_id):
    if request.method == 'POST':
        evenement = get_object_or_404(EvenementFamilial, id=event_id)
        texte = request.POST.get('texte', '').strip()
        if texte:
            Commentaire.objects.create(evenement=evenement, auteur=request.user, texte=texte)
    return redirect('home')

@login_required
def reacter_evenement(request, event_id):
    if request.method == 'POST':
        evenement = get_object_or_404(EvenementFamilial, id=event_id)
        type_reac = request.POST.get('type_reaction', 'LIKE')
        if type_reac in dict(Reaction.TYPES):
            Reaction.objects.get_or_create(evenement=evenement, utilisateur=request.user, type_reaction=type_reac)
    return redirect('home')
