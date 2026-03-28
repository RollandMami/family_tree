from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import EvenementForm

@login_required
def creer_evenement(request):
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            evenement = form.save(commit=False)
            evenement.organisateur = request.user # On lie l'auteur
            evenement.save()
            form.save_m2m() # Important pour les participants (Many-to-Many)
    return redirect('home')
