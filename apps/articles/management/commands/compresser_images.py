import os
import sys
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image

from apps.articles.models import Article, ImageArticle, Categorie, Configuration


def compresser_fichier_image(champ_image, largeur_max=1200, qualite=80):
    """
    Ouvre le fichier déjà stocké derrière un ImageField, le compresse/convertit
    en JPEG, et retourne (nouveau_contenu, nouveau_nom, taille_avant, taille_apres)
    ou None si rien à faire (déjà petit, ou fichier introuvable).
    """
    if not champ_image or not champ_image.name:
        return None

    try:
        taille_avant = champ_image.size
    except (FileNotFoundError, ValueError):
        return None

    # Seuil : on ne touche pas aux fichiers déjà légers
    if taille_avant <= 300 * 1024:
        return None

    try:
        champ_image.open('rb')
        img = Image.open(champ_image)
        img.load()
    except Exception as e:
        return None
    finally:
        champ_image.close()

    if img.mode != 'RGB':
        img = img.convert('RGB')

    if img.width > largeur_max:
        ratio = largeur_max / img.width
        nouvelle_hauteur = int(img.height * ratio)
        img = img.resize((largeur_max, nouvelle_hauteur), Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=qualite, optimize=True)
    taille_apres = buffer.tell()
    buffer.seek(0)

    nom_base = os.path.splitext(champ_image.name)[0]
    nouveau_nom = nom_base + '.jpg'

    return ContentFile(buffer.read()), nouveau_nom, taille_avant, taille_apres


class Command(BaseCommand):
    help = "Recompresse en JPEG toutes les images déjà uploadées (articles, galerie, catégories, config du site)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Simule sans rien modifier, affiche juste ce qui serait fait.",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        total_avant = 0
        total_apres = 0
        compteur = 0

        def traiter(instance, champ_nom, largeur_max=1200):
            nonlocal total_avant, total_apres, compteur
            champ_image = getattr(instance, champ_nom)
            resultat = compresser_fichier_image(champ_image, largeur_max=largeur_max)
            if resultat is None:
                return
            contenu, nouveau_nom, avant, apres = resultat
            self.stdout.write(
                f"  {champ_image.name} : {avant/1024:.0f} Ko -> {apres/1024:.0f} Ko"
            )
            total_avant += avant
            total_apres += apres
            compteur += 1
            if not dry_run:
                ancien_nom = champ_image.name
                champ_image.save(nouveau_nom, contenu, save=True)
                # Supprime l'ancien fichier si le nom a changé (png -> jpg)
                if ancien_nom != champ_image.name:
                    champ_image.storage.delete(ancien_nom)

        self.stdout.write(self.style.NOTICE("Articles (image_principale)..."))
        for article in Article.objects.exclude(image_principale=''):
            traiter(article, 'image_principale', largeur_max=1200)

        self.stdout.write(self.style.NOTICE("Galerie d'articles..."))
        for img in ImageArticle.objects.exclude(image=''):
            traiter(img, 'image', largeur_max=1600)

        self.stdout.write(self.style.NOTICE("Catégories..."))
        for cat in Categorie.objects.exclude(image=''):
            traiter(cat, 'image', largeur_max=1200)

        self.stdout.write(self.style.NOTICE("Configuration du site (logo, image_partage)..."))
        config = Configuration.objects.filter(pk=1).first()
        if config:
            traiter(config, 'logo', largeur_max=800)
            traiter(config, 'image_partage', largeur_max=1200)
            # favicon volontairement exclu

        self.stdout.write(self.style.SUCCESS(
            f"\n{compteur} image(s) traitée(s). "
            f"Total : {total_avant/1024/1024:.2f} Mo -> {total_apres/1024/1024:.2f} Mo"
        ))
        if dry_run:
            self.stdout.write(self.style.WARNING("Mode --dry-run : aucune modification enregistrée."))