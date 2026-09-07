#!/bin/bash
set -e
echo "=== Installation enoschofficiel ==="
python -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "=== Création de la base de données MySQL ==="
mysql -u root -e "CREATE DATABASE IF NOT EXISTS lemedia_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || echo "Créez la base manuellement si MySQL n'est pas configuré."
echo "=== Migrations ==="
python manage.py migrate
echo "=== Collecte des fichiers statiques ==="
python manage.py collectstatic --noinput
echo "=== Création du superutilisateur ==="
python manage.py createsuperuser
echo "=== Démarrage ==="
python manage.py runserver
