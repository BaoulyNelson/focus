from django.contrib import admin
from .models import Article, Categorie, Tag, ImageArticle, Configuration


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


class ImageArticleInline(admin.TabularInline):
    model = ImageArticle
    extra = 3


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
    inlines         = [ImageArticleInline]


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Empeche de creer une deuxieme ligne : singleton force via pk=1
        return not Configuration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False