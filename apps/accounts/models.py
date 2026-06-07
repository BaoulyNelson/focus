from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('lecteur',  'Lecteur'),
        ('auteur',   'Auteur'),
        ('editeur',  'Editeur'),
    ]

    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    bio       = models.TextField(max_length=500, blank=True, verbose_name='Biographie')
    avatar    = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Photo de profil')
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lecteur', verbose_name='Role')
    site_web  = models.URLField(blank=True, verbose_name='Site web')
    twitter   = models.CharField(max_length=100, blank=True, verbose_name='Twitter')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'

    def __str__(self):
        return f"Profil de {self.user.get_full_name() or self.user.username}"

    def get_absolute_url(self):
        return reverse('accounts:profil', kwargs={'username': self.user.username})

    @property
    def can_write(self):
        return self.role in ['auteur', 'editeur'] or self.user.is_staff

    @property
    def can_manage(self):
        return self.role == 'editeur' or self.user.is_staff

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/default-avatar.png'
