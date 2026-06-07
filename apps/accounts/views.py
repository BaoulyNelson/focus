from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import login
from .forms import FormulaireConnexion, FormulaireInscription, FormulaireModificationProfil
from .models import UserProfile


class VueConnexion(LoginView):
    template_name = 'accounts/connexion.html'
    form_class    = FormulaireConnexion
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request,
            f"Bienvenue, {user.get_full_name() or user.username} !")
        return super().form_valid(form)


class VueDeconnexion(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Vous avez ete deconnecte avec succes.')
        return super().dispatch(request, *args, **kwargs)


class VueInscription(CreateView):
    template_name = 'accounts/inscription.html'
    form_class    = FormulaireInscription
    success_url   = reverse_lazy('articles:accueil')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('articles:accueil')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Votre compte a ete cree avec succes. Bienvenue !')
        return redirect(self.success_url)


class VueProfil(DetailView):
    template_name      = 'accounts/profil.html'
    context_object_name = 'profil_user'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['articles'] = self.get_object().article_set.filter(
            status='publie').order_by('-published_at')[:6]
        return ctx


class VueModifierProfil(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/modifier_profil.html'
    form_class    = FormulaireModificationProfil

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        u = self.request.user
        form.fields['first_name'].initial = u.first_name
        form.fields['last_name'].initial  = u.last_name
        form.fields['email'].initial      = u.email
        return form

    def form_valid(self, form):
        form.save()
        u = self.request.user
        u.first_name = form.cleaned_data['first_name']
        u.last_name  = form.cleaned_data['last_name']
        u.email      = form.cleaned_data['email']
        u.save()
        messages.success(self.request, 'Votre profil a ete mis a jour avec succes.')
        return redirect('accounts:profil', username=u.username)
