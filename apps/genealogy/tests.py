from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from apps.genealogy.models import Personne, Couple


class TreeViewTests(TestCase):
    def setUp(self):
        # Création de l'utilisateur pour accéder à la vue protégée
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Couple racine
        self.dadafara = Personne.objects.create(prenom='Dadafara', nom='REKOTONDRAFARA', genre='H')
        self.isabelle = Personne.objects.create(prenom='Isabelle', nom='RAHARIMALALA', genre='F')
        Couple.objects.create(homme=self.dadafara, femme=self.isabelle, statut='MARIE')

        # Descendant
        self.adolphe = Personne.objects.create(
            prenom='Adolphe', nom='RAKOTOARISON', genre='H',
            pere_bio=self.dadafara, mere_bio=self.isabelle
        )

        # Conjointe du descendant (ne doit pas être racine)
        self.joely = Personne.objects.create(prenom='Joely Arisoa', nom='RAZAFIARIVELO', genre='F')
        Couple.objects.create(homme=self.adolphe, femme=self.joely, statut='MARIE')

    def test_tree_view_exclut_conjoint_de_descendant(self):
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('tree_view'))
        self.assertEqual(response.status_code, 200)

        racines = list(response.context['racines'])

        # Vérifier qu'il y a un seul tronc racine (la première génération uniquement)
        self.assertEqual(len(racines), 1)
        self.assertEqual(racines[0], self.dadafara)

        # Joely ne doit pas apparaître comme racine
        self.assertNotIn(self.joely, racines)


class PersonneRelationTests(TestCase):
    def setUp(self):
        self.grand_pere = Personne.objects.create(prenom='Grand', nom='Pere', genre='H')
        self.grand_mere = Personne.objects.create(prenom='Grand', nom='Mere', genre='F')
        self.pere = Personne.objects.create(prenom='Pere', nom='Fils', genre='H', pere_bio=self.grand_pere, mere_bio=self.grand_mere)
        self.mere = Personne.objects.create(prenom='Mere', nom='Fille', genre='F')
        self.oncle = Personne.objects.create(prenom='Oncle', nom='Cousin', genre='H', pere_bio=self.grand_pere, mere_bio=self.grand_mere)
        self.enfant = Personne.objects.create(prenom='Enfant', nom='Ni', genre='H', pere_bio=self.pere, mere_bio=self.mere)

    def test_relation_frere(self):
        frere = Personne.objects.create(prenom='Frere', nom='Du', genre='H', pere_bio=self.pere.pere_bio, mere_bio=self.pere.mere_bio)
        self.assertEqual(self.pere.get_relation_to(frere), 'frere')

    def test_relation_cousin(self):
        # cousin du point de vue de l'enfant de self.pere
        cousin = Personne.objects.create(prenom='Cousin', nom='Random', genre='H', pere_bio=self.oncle, mere_bio=Personne.objects.create(prenom='Amie', nom='Dupont', genre='F'))
        self.assertEqual(self.enfant.get_relation_to(cousin), 'cousin')

    def test_relation_niece_neveu(self):
        niece = Personne.objects.create(prenom='Niece', nom='Test', genre='F', pere_bio=self.oncle, mere_bio=self.mere)
        self.assertEqual(self.pere.get_relation_to(niece), 'niece_neveu')

    def test_relation_distant(self):
        stranger = Personne.objects.create(prenom='Stranger', nom='Inconnu', genre='H')
        self.assertEqual(self.pere.get_relation_to(stranger), 'distant')
