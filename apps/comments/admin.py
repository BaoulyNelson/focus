from django.contrib import admin
from .models import Commentaire


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display  = ('auteur', 'article', 'is_approved', 'created_at', 'apercu')
    list_filter   = ('is_approved', 'created_at')
    search_fields = ('auteur__username', 'contenu', 'article__titre')
    list_editable = ('is_approved',)
    date_hierarchy = 'created_at'
    actions = ['approuver', 'masquer']

    def apercu(self, obj):
        return obj.contenu[:80]
    apercu.short_description = 'Contenu'

    def approuver(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} commentaire(s) approuve(s).')
    approuver.short_description = 'Approuver la selection'

    def masquer(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} commentaire(s) masque(s).')
    masquer.short_description = 'Masquer la selection'
