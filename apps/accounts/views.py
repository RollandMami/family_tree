from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.accounts.forms import InscriptionForm, UserUpdateForm, PersonneUpdateForm, MediaForm
from apps.gallery.models import Media
from apps.genealogy.models import Personne


def register(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username} ! Vous pouvez vous connecter.')
            return redirect('login')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    profile = getattr(user, 'profile', None)

    # assure une personne rattachée au profile
    if not profile:
        messages.warning(request, "Aucun profil n'est associé à votre compte. Veuillez contacter un administrateur.")
        return redirect('home')

    personne = profile.personne
    if not personne:
        personne = Personne.objects.create(
            nom=user.last_name or user.username,
            prenom=user.first_name or user.username,
            genre='H' if user.last_name else 'F',
            email=user.email,
        )
        profile.personne = personne
        profile.save()

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        personne_form = PersonneUpdateForm(request.POST, request.FILES, instance=personne)
        media_form = MediaForm(request.POST, request.FILES)

        if user_form.is_valid() and personne_form.is_valid():
            user_form.save()
            personne = personne_form.save()

            if media_form.is_valid() and media_form.cleaned_data.get('fichier'):
                media = media_form.save(commit=False)
                media.personne = personne
                media.save()

            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        user_form = UserUpdateForm(instance=user)
        personne_form = PersonneUpdateForm(instance=personne)
        media_form = MediaForm()

    medias = personne.galerie.all() if personne else Media.objects.none()

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'personne_form': personne_form,
        'media_form': media_form,
        'medias': medias,
    })
