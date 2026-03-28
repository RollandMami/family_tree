from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from apps.genealogy.models import Personne
from apps.notifications.models import Notification
from apps.events.models import EvenementFamilial, Commentaire, Reaction


class NotificationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='pass')
        self.user2 = User.objects.create_user(username='bob', password='pass')

    def test_notification_creation_ajout_personne(self):
        Personne.objects.create(prenom='Pierre', nom='Dupont', genre='H', est_en_vie=True)
        self.assertTrue(Notification.objects.filter(type_notif='SYSTEME', titre__icontains='Nouvelle personne').exists())

    def test_notification_creation_deces(self):
        p = Personne.objects.create(prenom='Jacques', nom='Martin', genre='H', est_en_vie=True)
        p.est_en_vie = False
        p.date_deces = '2026-03-28'
        p.save()
        self.assertTrue(Notification.objects.filter(type_notif='DECES', titre__icontains='décédé').exists())

    def test_notification_creation_evenement(self):
        participant = Personne.objects.create(prenom='Nina', nom='Bernard', genre='F', est_en_vie=True)
        self.client.login(username='alice', password='pass')
        data = {
            'titre': 'Anniversaire de Fête',
            'type_evt': 'REUNION',
            'date_evenement': '2026-04-01',
            'description': 'Grande réunion',
            'lieu': 'Maison',
            'participants': [participant.id],
        }
        response = self.client.post(reverse('creer_evenement'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Notification.objects.filter(type_notif='EVENEMENT', titre__icontains='Nouvel événement').exists())

    def test_notification_creation_commentaire(self):
        event = EvenementFamilial.objects.create(
            titre='Réunion',
            type_evt='REUNION',
            date_evenement='2026-05-01',
            organisateur=self.user1,
        )
        self.client.login(username='bob', password='pass')
        response = self.client.post(reverse('commenter_evenement', args=[event.id]), {'texte': 'Super!',})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Notification.objects.filter(type_notif='COMMENTAIRE', destinataire=self.user1).exists())

    def test_notification_creation_reaction(self):
        event = EvenementFamilial.objects.create(
            titre='Réunion',
            type_evt='REUNION',
            date_evenement='2026-05-01',
            organisateur=self.user1,
        )
        self.client.login(username='bob', password='pass')
        response = self.client.post(reverse('reacter_evenement', args=[event.id]), {'type_reaction': 'LIKE'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Notification.objects.filter(type_notif='REACTION', destinataire=self.user1).exists())

    def test_navbar_unread_badge(self):
        Notification.objects.create(destinataire=self.user1, titre='Test', message='Test', type_notif='SYSTEME')
        self.client.login(username='alice', password='pass')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'badge')
        self.assertContains(response, '1')

    def test_notifications_page_accessible(self):
        self.client.login(username='alice', password='pass')
        response = self.client.get(reverse('notifications_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Notification Famille')

# Create your tests here.
