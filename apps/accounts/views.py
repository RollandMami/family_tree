from django.shortcuts import render, redirect
from django.contrib import messages
from apps.accounts.forms import InscriptionForm

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


def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
