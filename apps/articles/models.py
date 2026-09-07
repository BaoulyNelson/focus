from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import F
import re
from ckeditor_uploader.fields import RichTextUploadingField


class Categorie(models.Model):
    nom         = models.CharField(max_length=100, unique=True, verbose_name='Nom')
    slug        = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Description')
    image       = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Image')
    couleur     = models.CharField(max_length=7, default='#e74c3c', verbose_name='Couleur')
    ordre       = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categories'
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articles:categorie', kwargs={'slug': self.slug})

    @property
    def nombre_articles(self):
        return self.articles.filter(status='publie').count()


class Tag(models.Model):
    nom  = models.CharField(max_length=50, unique=True, verbose_name='Nom')
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articles:tag', kwargs={'slug': self.slug})


class Article(models.Model):
    STATUS_CHOICES = [
        ('brouillon',  'Brouillon'),
        ('en_revision', 'En revision'),
        ('publie',     'Publie'),
    ]

    titre            = models.CharField(max_length=255, verbose_name='Titre')
    slug             = models.SlugField(max_length=280, unique=True, blank=True)
    contenu = RichTextUploadingField(verbose_name='Contenu')
    extrait          = models.TextField(max_length=400, blank=True, verbose_name='Extrait')
    image_principale = models.ImageField(upload_to='articles/%Y/%m/', blank=True, null=True,
                                         verbose_name='Image principale')
    auteur    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  related_name='article_set', verbose_name='Auteur')
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='articles', verbose_name='Categorie')
    tags      = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name='Tags')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                      default='brouillon', verbose_name='Statut')
    est_a_la_une   = models.BooleanField(default=False, verbose_name='Article a la une')
    est_breaking   = models.BooleanField(default=False, verbose_name='Breaking news')
    nombre_vues    = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    created_at     = models.DateTimeField(auto_now_add=True, verbose_name='Date de creation')
    updated_at     = models.DateTimeField(auto_now=True,     verbose_name='Derniere modification')
    published_at   = models.DateTimeField(null=True, blank=True, verbose_name='Date de publication')

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titre)
            slug = base
            n = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        if not self.extrait and self.contenu:
            clean = re.sub(r'<[^>]+>', '', self.contenu)
            self.extrait = clean[:300] + '...' if len(clean) > 300 else clean
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})

    def incrementer_vues(self):
        Article.objects.filter(pk=self.pk).update(nombre_vues=F('nombre_vues') + 1)

    @property
    def nombre_commentaires(self):
        return self.commentaire_set.filter(is_approved=True).count()

    @property
    def temps_lecture(self):
        mots = len(re.sub(r'<[^>]+>', '', self.contenu or '').split())
        return f"{max(1, round(mots / 200))} min"
    
    
    
    
from django.conf import settings
from django.core.cache import cache

class Configuration(models.Model):
    site_name        = models.CharField(max_length=100, verbose_name='Nom du site')
    site_description = models.CharField(max_length=255, blank=True, verbose_name='Description')
    site_tagline     = models.CharField(max_length=255, blank=True, verbose_name='Slogan')
    contact_email    = models.EmailField(blank=True, verbose_name='Email de contact')

    logo           = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name='Logo')
    favicon        = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name='Favicon (carré, ex: 512x512)')
    image_partage  = models.ImageField(upload_to='site/', blank=True, null=True,
                                        verbose_name='Image de partage par défaut',
                                        help_text='Utilisée quand un lien du site est partagé sans image propre. Idéal: 1200x630px.')

    facebook_url  = models.URLField(blank=True, verbose_name='Facebook')
    twitter_url   = models.URLField(blank=True, verbose_name='Twitter / X')
    instagram_url = models.URLField(blank=True, verbose_name='Instagram')
    youtube_url   = models.URLField(blank=True, verbose_name='YouTube')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuration du site'
        verbose_name_plural = 'Configuration du site'

    def __str__(self):
        return 'Configuration du site'

    def save(self, *args, **kwargs):
        self.pk = 1  # force le singleton : une seule ligne, toujours id=1
        super().save(*args, **kwargs)
        cache.delete('site_config')

    def delete(self, *args, **kwargs):
        pass  # empêche la suppression accidentelle

    @classmethod
    def get(cls):
        config = cache.get('site_config')
        if not config:
            config, _ = cls.objects.get_or_create(pk=1, defaults={
                'site_name':        settings.SITE_NAME,
                'site_description': settings.SITE_DESCRIPTION,
                'site_tagline':     settings.SITE_TAGLINE,
                'contact_email':    settings.CONTACT_EMAIL,
            })
            cache.set('site_config', config, None)
        return config
