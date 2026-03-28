from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.events.models import EvenementFamilial, Commentaire
from apps.genealogy.models import Personne


class EvenementCommentaireEditionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.personne = Personne.objects.create(nom='Dupont', prenom='Jean', genre='H')
        self.event = EvenementFamilial.objects.create(
            titre='Fête',
            type_evt='AUTRE',
            date_evenement='2025-09-01',
            description='Ancienne description',
            lieu='Maison',
            organisateur=self.user1,
        )
        self.event.participants.add(self.personne)

        self.commentaire = Commentaire.objects.create(evenement=self.event, auteur=self.user2, texte='Premier commentaire')

    def test_edit_event_by_owner(self):
        self.client.login(username='user1', password='pass')
        url = reverse('modifier_evenement', args=[self.event.id])
        with open('/tmp/test_image.jpg', 'wb') as f:
            f.write(b'\x47\x49\x46\x38\x39\x61')
        response = self.client.post(url, {
            'titre': 'Fête mise à jour',
            'type_evt': 'AUTRE',
            'date_evenement': '2025-09-01',
            'description': 'Nouvelle description',
            'lieu': 'Nouveau lieu',
            'participants': [self.personne.id],
        }, follow=True)
        self.event.refresh_from_db()
        self.assertEqual(self.event.description, 'Nouvelle description')
        self.assertEqual(self.event.lieu, 'Nouveau lieu')
        self.assertEqual(response.status_code, 200)

    def test_edit_event_not_owner(self):
        self.client.login(username='user2', password='pass')
        url = reverse('modifier_evenement', args=[self.event.id])
        response = self.client.post(url, {
            'titre': 'Tentative',
            'type_evt': 'AUTRE',
            'date_evenement': '2025-09-01',
            'description': 'Ne devrait pas fonctionner',
            'lieu': 'Lieu',
            'participants': [],
        }, follow=True)
        self.event.refresh_from_db()
        self.assertEqual(self.event.description, 'Ancienne description')

    def test_edit_own_commentaire(self):
        self.client.login(username='user2', password='pass')
        url = reverse('modifier_commentaire', args=[self.commentaire.id])
        response = self.client.post(url, {'texte': 'Commentaire modifié'}, follow=True)
        self.commentaire.refresh_from_db()
        self.assertEqual(self.commentaire.texte, 'Commentaire modifié')

    def test_edit_commentaire_not_author(self):
        self.client.login(username='user1', password='pass')
        url = reverse('modifier_commentaire', args=[self.commentaire.id])
        response = self.client.post(url, {'texte': 'Tentative'}, follow=True)
        self.commentaire.refresh_from_db()
        self.assertEqual(self.commentaire.texte, 'Premier commentaire')

