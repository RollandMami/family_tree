from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.events.utils import obtenir_agenda_proche
from apps.notifications.models import Notification

class Command(BaseCommand):
    help = "Génère les notifications pour les événements à J-5"

    def handle(self, *args, **options):
        agenda = obtenir_agenda_proche(jours=5)
        utilisateurs = User.objects.all()

        for user in utilisateurs:
            # Pour chaque anniversaire de naissance
            for perso in agenda['anniversaires']:
                Notification.objects.get_or_create(
                    destinataire=user,
                    titre=f"🎂 Anniversaire de {perso.prenom}",
                    message=f"C'est l'anniversaire de {perso.prenom} {perso.nom} bientôt !",
                    type_notif='ANNIVERSAIRE'
                )
            
            # Idem pour les décès et autres événements...
            self.stdout.write(self.style.SUCCESS(f"Notifications générées pour {user.username}"))