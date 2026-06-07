from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.core.cache import cache
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .models import Article, Categorie, Tag
from .forms import FormulaireArticle, FormulaireCategorieAdmin


# ── Mixins de permission ──────────────────────────────────────────────────────

class EditeurRequisMixin(LoginRequiredMixin):
    login_url = '/comptes/connexion/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Connectez-vous pour acceder a cette page.')
            return self.handle_no_permission()
        try:
            if not (request.user.userprofile.can_write or request.user.is_staff):
                raise PermissionDenied("Acces refuse.")
        except AttributeError:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class GestionnaireRequisMixin(LoginRequiredMixin):
    login_url = '/comptes/connexion/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            if not (request.user.userprofile.can_manage or request.user.is_staff):
                raise PermissionDenied
        except AttributeError:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# ── Vues publiques ────────────────────────────────────────────────────────────

class VueAccueil(ListView):
    template_name       = 'articles/accueil.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.objects.filter(status='publie').select_related(
            'auteur', 'categorie', 'auteur__userprofile'
        ).prefetch_related('tags')[:12]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cached = cache.get('accueil_ctx')
        if not cached:
            qs = Article.objects.filter(status='publie').select_related('auteur', 'categorie', 'auteur__userprofile')
            cached = {
                'article_une':        qs.filter(est_a_la_une=True).first(),
                'articles_une':       qs.filter(est_a_la_une=True)[:4],
                'articles_recents':   qs[:9],
                'articles_populaires': qs.order_by('-nombre_vues')[:5],
                'toutes_categories':  list(Categorie.objects.all()[:8]),
            }
            cache.set('accueil_ctx', cached, 120)
        ctx.update(cached)
        return ctx


class VueListeArticles(ListView):
    template_name       = 'articles/liste.html'
    context_object_name = 'articles'

    def get_paginate_by(self, queryset):
        from django.conf import settings
        return settings.ARTICLES_PER_PAGE

    def get_queryset(self):
        return Article.objects.filter(status='publie').select_related(
            'auteur', 'categorie', 'auteur__userprofile'
        ).prefetch_related('tags')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories']  = Categorie.objects.all()
        ctx['titre_page']  = 'Toutes les actualites'
        return ctx


from django.http import Http404
from django.db.models import F

class VueDetailArticle(DetailView):
    template_name       = 'articles/detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        # Queryset de base sans filtre statut — le filtrage se fait dans get_object
        return Article.objects.select_related(
            'auteur', 'categorie', 'auteur__userprofile'
        ).prefetch_related('tags')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.status == 'publie':
            obj.incrementer_vues()
            return obj

        # Brouillon / révision → staff ou auteur uniquement
        user = self.request.user
        if user.is_authenticated and (user.is_staff or obj.auteur == user):
            return obj  # pas d'incrément de vues pour les aperçus

        raise Http404

    def get_context_data(self, **kwargs):
        from apps.comments.forms import FormulaireCommentaire
        ctx = super().get_context_data(**kwargs)
        art = self.object

        similaires = Article.objects.filter(
            status='publie', categorie=art.categorie
        ).exclude(pk=art.pk).select_related('auteur', 'categorie')[:3]
        if not similaires:
            similaires = Article.objects.filter(
                status='publie'
            ).exclude(pk=art.pk).order_by('-published_at')[:3]

        ctx['articles_similaires']    = similaires
        ctx['formulaire_commentaire'] = FormulaireCommentaire()
        ctx['commentaires']           = art.commentaire_set.filter(
            is_approved=True, parent__isnull=True
        ).select_related('auteur', 'auteur__userprofile').prefetch_related('replies')
        ctx['articles_populaires']    = Article.objects.filter(
            status='publie').order_by('-nombre_vues')[:5]
        return ctx


class VueCategorieArticles(ListView):
    template_name       = 'articles/categorie.html'
    context_object_name = 'articles'
    paginate_by         = 9

    def get_queryset(self):
        self.categorie = get_object_or_404(Categorie, slug=self.kwargs['slug'])
        return Article.objects.filter(
            status='publie', categorie=self.categorie
        ).select_related('auteur', 'categorie', 'auteur__userprofile')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categorie']  = self.categorie
        ctx['categories'] = Categorie.objects.all()
        return ctx


class VueTagArticles(ListView):
    template_name       = 'articles/tag.html'
    context_object_name = 'articles'
    paginate_by         = 9

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Article.objects.filter(
            status='publie', tags=self.tag
        ).select_related('auteur', 'categorie', 'auteur__userprofile')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tag'] = self.tag
        return ctx


class VueRecherche(ListView):
    template_name       = 'articles/recherche.html'
    context_object_name = 'articles'
    paginate_by         = 9

    def get_queryset(self):
        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            return Article.objects.filter(
                Q(titre__icontains=self.query) |
                Q(extrait__icontains=self.query) |
                Q(tags__nom__icontains=self.query),
                status='publie'
            ).distinct().select_related('auteur', 'categorie')
        return Article.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query']            = self.query
        ctx['nombre_resultats'] = self.get_queryset().count()
        return ctx


# ── Tableau de bord ───────────────────────────────────────────────────────────

class VueTableauBord(EditeurRequisMixin, TemplateView):
    template_name = 'dashboard/accueil.html'

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        user = self.request.user
        is_gestionnaire = user.is_staff or (
            hasattr(user, 'userprofile') and user.userprofile.can_manage
        )
        articles = Article.objects.all() if is_gestionnaire else Article.objects.filter(auteur=user)
        ctx.update({
            'total_articles':    articles.count(),
            'articles_publies':  articles.filter(status='publie').count(),
            'articles_brouillons': articles.filter(status='brouillon').count(),
            'articles_recents':  articles.select_related('categorie').order_by('-created_at')[:5],
            'is_gestionnaire':   is_gestionnaire,
            'total_categories':  Categorie.objects.count(),
        })
        from apps.comments.models import Commentaire
        if is_gestionnaire:
            ctx['total_commentaires'] = Commentaire.objects.count()
            ctx['commentaires_recents'] = Commentaire.objects.select_related(
                'auteur', 'article').order_by('-created_at')[:5]
        else:
            ids = articles.values_list('id', flat=True)
            ctx['total_commentaires']   = Commentaire.objects.filter(article_id__in=ids).count()
            ctx['commentaires_recents'] = Commentaire.objects.filter(
                article_id__in=ids).select_related('auteur', 'article').order_by('-created_at')[:5]
        return ctx


class VueDashboardArticles(EditeurRequisMixin, ListView):
    template_name       = 'dashboard/articles/liste.html'
    context_object_name = 'articles'
    paginate_by         = 15

    def get_queryset(self):
        user = self.request.user
        qs = (Article.objects.all() if (user.is_staff or (
            hasattr(user, 'userprofile') and user.userprofile.can_manage
        )) else Article.objects.filter(auteur=user))
        st = self.request.GET.get('status')
        if st:
            qs = qs.filter(status=st)
        return qs.select_related('auteur', 'categorie').order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_filtre'] = self.request.GET.get('status', '')
        return ctx


class VueDashboardCreerArticle(EditeurRequisMixin, CreateView):
    template_name = 'dashboard/articles/formulaire.html'
    form_class    = FormulaireArticle
    success_url   = reverse_lazy('articles:dashboard_articles')

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['user'] = self.request.user
        return kw

    def form_valid(self, form):
        messages.success(self.request, 'Article cree avec succes !')
        cache.delete('accueil_ctx')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la creation. Corrigez les erreurs ci-dessous.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre_page']    = 'Creer un article'
        ctx['bouton_submit'] = "Creer l'article"
        return ctx


class VueDashboardModifierArticle(EditeurRequisMixin, UpdateView):
    template_name = 'dashboard/articles/formulaire.html'
    form_class    = FormulaireArticle
    success_url   = reverse_lazy('articles:dashboard_articles')

    def get_queryset(self):
        user = self.request.user
        return (Article.objects.all() if (user.is_staff or (
            hasattr(user, 'userprofile') and user.userprofile.can_manage
        )) else Article.objects.filter(auteur=user))

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['user'] = self.request.user
        return kw

    def form_valid(self, form):
        messages.success(self.request, 'Article mis a jour avec succes !')
        cache.delete('accueil_ctx')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la modification.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre_page']    = f"Modifier : {self.object.titre}"
        ctx['bouton_submit'] = 'Enregistrer les modifications'
        return ctx


class VueDashboardSupprimerArticle(EditeurRequisMixin, DeleteView):
    template_name = 'dashboard/articles/confirmer_suppression.html'
    success_url   = reverse_lazy('articles:dashboard_articles')

    def get_queryset(self):
        user = self.request.user
        return (Article.objects.all() if (user.is_staff or (
            hasattr(user, 'userprofile') and user.userprofile.can_manage
        )) else Article.objects.filter(auteur=user))

    def form_valid(self, form):
        messages.success(self.request, 'Article supprime avec succes.')
        cache.delete('accueil_ctx')
        return super().form_valid(form)


class VueDashboardCategories(GestionnaireRequisMixin, ListView):
    template_name       = 'dashboard/categories/liste.html'
    context_object_name = 'categories'
    queryset            = Categorie.objects.all()


class VueDashboardCreerCategorie(GestionnaireRequisMixin, CreateView):
    template_name = 'dashboard/categories/formulaire.html'
    form_class    = FormulaireCategorieAdmin
    success_url   = reverse_lazy('articles:dashboard_categories')

    def form_valid(self, form):
        messages.success(self.request, 'Categorie creee avec succes !')
        cache.delete('nav_categories')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre_page'] = 'Nouvelle categorie'
        return ctx


class VueDashboardModifierCategorie(GestionnaireRequisMixin, UpdateView):
    template_name = 'dashboard/categories/formulaire.html'
    form_class    = FormulaireCategorieAdmin
    queryset      = Categorie.objects.all()
    success_url   = reverse_lazy('articles:dashboard_categories')

    def form_valid(self, form):
        messages.success(self.request, 'Categorie mise a jour !')
        cache.delete('nav_categories')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre_page'] = f"Modifier : {self.object.nom}"
        return ctx


class VueDashboardSupprimerCategorie(GestionnaireRequisMixin, DeleteView):
    template_name = 'dashboard/categories/confirmer_suppression.html'
    queryset      = Categorie.objects.all()
    success_url   = reverse_lazy('articles:dashboard_categories')

    def form_valid(self, form):
        messages.success(self.request, 'Categorie supprimee.')
        cache.delete('nav_categories')
        return super().form_valid(form)


# ── Gestionnaires d'erreurs ───────────────────────────────────────────────────

def erreur_404(request, exception):
    return render(request, '404.html', status=404)

def erreur_500(request):
    return render(request, '500.html', status=500)
