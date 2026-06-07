from django.db import models
from django.contrib.auth.models import User
from apps.articles.models import Article


class Commentaire(models.Model):
    article    = models.ForeignKey(Article, on_delete=models.CASCADE,
                                   related_name='commentaire_set', verbose_name='Article')
    auteur     = models.ForeignKey(User,    on_delete=models.CASCADE,
                                   related_name='commentaires',    verbose_name='Auteur')
    contenu    = models.TextField(max_length=2000, verbose_name='Commentaire')
    parent     = models.ForeignKey('self', on_delete=models.CASCADE,
                                   null=True, blank=True, related_name='replies',
                                   verbose_name='Reponse a')
    is_approved = models.BooleanField(default=True, verbose_name='Approuve')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['created_at']

    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur {self.article.titre[:30]}"
