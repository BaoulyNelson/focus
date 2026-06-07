from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # ── Vues publiques ─────────────────────────────────────────────────────────
    path('',                        views.VueAccueil.as_view(),       name='accueil'),
    path('actualites/',             views.VueListeArticles.as_view(), name='liste'),
    path('article/<slug:slug>/',    views.VueDetailArticle.as_view(), name='detail'),
    path('categorie/<slug:slug>/',  views.VueCategorieArticles.as_view(), name='categorie'),
    path('tag/<slug:slug>/',        views.VueTagArticles.as_view(),   name='tag'),
    path('recherche/',              views.VueRecherche.as_view(),     name='recherche'),
    # ── Tableau de bord ────────────────────────────────────────────────────────
    path('tableau-de-bord/',
         views.VueTableauBord.as_view(), name='dashboard'),
    path('tableau-de-bord/articles/',
         views.VueDashboardArticles.as_view(), name='dashboard_articles'),
    path('tableau-de-bord/articles/nouveau/',
         views.VueDashboardCreerArticle.as_view(), name='dashboard_creer_article'),
    path('tableau-de-bord/articles/<int:pk>/modifier/',
         views.VueDashboardModifierArticle.as_view(), name='dashboard_modifier_article'),
    path('tableau-de-bord/articles/<int:pk>/supprimer/',
         views.VueDashboardSupprimerArticle.as_view(), name='dashboard_supprimer_article'),
    # ── Categories ─────────────────────────────────────────────────────────────
    path('tableau-de-bord/categories/',
         views.VueDashboardCategories.as_view(), name='dashboard_categories'),
    path('tableau-de-bord/categories/nouvelle/',
         views.VueDashboardCreerCategorie.as_view(), name='dashboard_creer_categorie'),
    path('tableau-de-bord/categories/<int:pk>/modifier/',
         views.VueDashboardModifierCategorie.as_view(), name='dashboard_modifier_categorie'),
    path('tableau-de-bord/categories/<int:pk>/supprimer/',
         views.VueDashboardSupprimerCategorie.as_view(), name='dashboard_supprimer_categorie'),
]
