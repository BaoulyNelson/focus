from django.contrib import admin
from .models import Article, Categorie, Tag


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display    = ('nom', 'slug', 'nombre_articles', 'ordre')
    prepopulated_fields = {'slug': ('nom',)}
    list_editable   = ('ordre',)
    search_fields   = ('nom',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display    = ('nom', 'slug')
    prepopulated_fields = {'slug': ('nom',)}
    search_fields   = ('nom',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display    = ('titre', 'auteur', 'categorie', 'status', 'est_a_la_une', 'nombre_vues', 'published_at')
    list_filter     = ('status', 'categorie', 'est_a_la_une', 'est_breaking')
    search_fields   = ('titre', 'contenu', 'auteur__username')
    prepopulated_fields = {'slug': ('titre',)}
    date_hierarchy  = 'published_at'
    list_editable   = ('status', 'est_a_la_une')
    filter_horizontal = ('tags',)
    readonly_fields = ('nombre_vues', 'created_at', 'updated_at')
