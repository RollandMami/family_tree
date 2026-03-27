# Famille Connectée - Plateforme de Généalogie Interactive

## 📝 Description
**Famille Connectée** est une application web basée sur Django permettant de créer, gérer et visualiser un arbre généalogique dynamique. Contrairement aux outils classiques, cette plateforme permet à chaque membre de la famille de posséder un compte utilisateur pour mettre à jour ses propres données (biographie, CV, réseaux sociaux, signes distinctifs) et interagir avec les événements familiaux (anniversaires, mariages, baptêmes).

Le projet gère les complexités biologiques et sociales telles que les parents adoptifs, les familles recomposées (unions multiples) et les statuts de vie/décès (en vie, mort, causes, dates).

---

## 👤 Author
* **Rolland** - *Développeur Backend & Concepteur BIM/CAD*

---

## 🏗 Structure du Projet
Le projet est découpé en applications modulaires pour une meilleure maintenance et séparation des responsabilités :

```text
famille_project/
├── core/                   # Configuration Django (settings, urls, wsgi)
├── media/                  # Stockage (Photos, Vidéos de présentation, CV PDF)
├── static/                 # Assets (CSS, JS pour D3.js, Images)
├── templates/              # Layouts HTML globaux et partagés
└── apps/
    ├── accounts/           # Authentification, Inscription et Profils Utilisateurs
    ├── genealogy/          # Cœur du projet : Personne, Couple, Signes distinctifs
    ├── events/             # Gestion des Naissances, Décès, Mariages, Baptêmes
    ├── notifications/      # Alertes (J-5 avant anniversaire, rappels d'événements)
    └── gallery/            # Gestion multi-médias (Albums photos et vidéos)

#⚙️ Installation / Exécution
Prérequis
    Python 3.10+
    Django 5.0+

    Environnement virtuel (venv)

Étapes

    Cloner le dépôt :
    Bash

    git clone [https://github.com/votre-compte/famille-connectee.git](https://github.com/votre-compte/famille-connectee.git)
    cd famille-connectee

    Créer et activer l'environnement virtuel :
    Bash

    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # ou venv\Scripts\activate pour Windows

    Installer les dépendances :
    Bash

    pip install django pillow django-cleanup
    # Ajoutez d'autres dépendances selon vos besoins

    Appliquer les migrations et lancer le serveur :
    Bash

    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

🧠 Algorithmes & Logique Relationnelle

Le projet repose sur plusieurs algorithmes clés pour assurer l'intégrité de l'arbre :

    Récursivité de Parenté : Utilisation de self (Self-referencing ForeignKey) pour lier les individus à leurs parents biologiques et adoptifs.

    Calcul des Liens Fraternels :

        Frères/Sœurs : Partage du même couple de parents biologiques.

        Demi-Frères/Sœurs : Partage d'un seul parent biologique via des unions différentes.

    Algorithme de Cousins : Recherche transversale remontant aux grands-parents communs via les clés étrangères parentales.

    Fenêtre de Notification (J-5) : Script de filtrage temporel calculant l'écart entre date.today() et date_evenement sans tenir compte de l'année (modulo annuel).

    Validation d'Intégrité : Vérification stricte que la date de décès est postérieure à la date de naissance et que l'âge des parents est cohérent avec celui des enfants.

📚 Ressources

    Framework : Django

    Base de données : SQLite (Développement) / PostgreSQL (Production)

    Visualisation d'Arbre : D3.js ou Cytoscape.js pour le rendu graphique des liens.

    Traitement d'Image : Pillow.

🚀 Améliorations Futures

    GEDCOM Import/Export : Compatibilité avec les standards mondiaux de généalogie.

    Niveaux de Confidentialité : Masquage sélectif des données sensibles (téléphone, adresse) selon le degré de parenté.

    Recherche par Signes Distinctifs : Moteur de recherche avancé (ex: "Retrouver mon cousin chauve").

    Galerie Vidéo : Application dédiée pour uploader plusieurs souvenirs par personne.
