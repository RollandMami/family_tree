from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings


def about_view(request):
    app_version = '1.0.0'
    auteur = {
        'nom': 'Ton Nom',
        'description': "Je suis un(e) développeur(se) passionné(e) par les applications familiales, l'expérience utilisateur et la gestion de la mémoire généalogique."
    }

    if request.method == 'POST':
        nom = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        sujet = request.POST.get('subject', 'Message depuis la page À propos').strip()
        message = request.POST.get('message', '').strip()

        if not nom or not email or not message:
            messages.error(request, "Merci de remplir tous les champs du formulaire de contact.")
            return redirect('about')

        corps = f"Message de {nom} ({email})\n\nSujet: {sujet}\n\n{message}"
        destinataire = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'admin@example.com'

        try:
            send_mail(sujet, corps, destinataire, [destinataire])
            messages.success(request, "Merci, votre message a bien été envoyé !")
        except BadHeaderError:
            messages.error(request, "Erreur d'envoi: en-tête invalide.")
        except Exception:
            messages.error(request, "Erreur lors de l'envoi du message. Vérifiez votre configuration email.")

        return redirect('about')

    context = {
        'app_version': app_version,
        'auteur': auteur,
    }
    return render(request, 'about.html', context)

