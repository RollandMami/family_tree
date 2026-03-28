from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from apps.notifications.models import Notification
from .forms import EvenementForm
from .models import EvenementFamilial, Commentaire, Reaction

@login_required
def creer_evenement(request):
    if request.method == 'POST':
        form = EvenementForm(request.POST, request.FILES)
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


@login_required
def supprimer_evenement(request, event_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('home')

    evenement = get_object_or_404(EvenementFamilial, id=event_id)
    if request.method == 'POST':
        evenement.delete()
    return redirect('home')


@login_required
def modifier_evenement(request, event_id):
    evenement = get_object_or_404(EvenementFamilial, id=event_id)
    if request.user != evenement.organisateur and not (request.user.is_staff or request.user.is_superuser):
        return redirect('home')

    if request.method == 'POST':
        form = EvenementForm(request.POST, request.FILES, instance=evenement)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EvenementForm(instance=evenement)

    return render(request, 'events/edit_event.html', {'form_event': form, 'evenement': evenement})


@login_required
def modifier_commentaire(request, comment_id):
    commentaire = get_object_or_404(Commentaire, id=comment_id)
    if request.user != commentaire.auteur and not (request.user.is_staff or request.user.is_superuser):
        return redirect('home')

    if request.method == 'POST':
        texte = request.POST.get('texte', '').strip()
        if texte:
            commentaire.texte = texte
            commentaire.save()
    return redirect('home')
