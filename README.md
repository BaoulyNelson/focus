# LeMédia — Site web d'information Django 4.2

## Prérequis
- Python 3.10+
- MySQL 8+ via XAMPP (ou MariaDB)
- XAMPP démarré (Apache + MySQL)

## Installation rapide

```bash
# 1. Dézipper le projet
cd lemedia

# 2. Créer la base de données dans phpMyAdmin ou MySQL CLI
mysql -u root -e "CREATE DATABASE lemedia_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 3. Environnement virtuel
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate.bat      # Windows

# 4. Dépendances
pip install -r requirements.txt

# 5. Variables d'environnement — éditer le fichier .env
# (DB_PASSWORD= si root sans mot de passe)

# 6. Migrations
python manage.py migrate

# 7. Superutilisateur (accès à /administration/)
python manage.py createsuperuser

# 8. Lancer
python manage.py runserver
```

Accès : http://127.0.0.1:8000

## Rôles utilisateurs

| Rôle      | Droits                                              |
|-----------|-----------------------------------------------------|
| Lecteur   | Lire et commenter                                   |
| Auteur    | Créer/modifier ses propres articles                 |
| Éditeur   | Gérer tous les articles, catégories, commentaires   |
| Superuser | Accès complet + interface Django Admin              |

## Changer le rôle d'un utilisateur
1. Via `/administration/` (superuser uniquement)
2. Ou via le tableau de bord Django Admin → Comptes → Profil utilisateur

## URLs principales
- `/` — Accueil
- `/actualites/` — Liste des articles
- `/article/<slug>/` — Détail article
- `/categorie/<slug>/` — Articles par catégorie
- `/recherche/?q=...` — Recherche
- `/contact/` — Formulaire de contact
- `/comptes/connexion/` — Connexion
- `/comptes/inscription/` — Inscription
- `/tableau-de-bord/` — Espace rédacteur/éditeur
- `/administration/` — Admin Django (superuser)

## Structure du projet
```
lemedia/
├── .env                  # Variables sensibles (ne pas versionner)
├── manage.py
├── requirements.txt
├── lemedia/              # Configuration Django
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── accounts/         # Authentification + profils
│   ├── articles/         # Articles, catégories, tags
│   ├── comments/         # Commentaires
│   └── contact/          # Formulaire de contact
├── templates/            # Templates HTML
├── static/               # CSS, JS
└── media/                # Uploads (images)
```
