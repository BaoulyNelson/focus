from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('connexion/',       views.VueConnexion.as_view(),      name='connexion'),
    path('deconnexion/',     views.VueDeconnexion.as_view(),    name='deconnexion'),
    path('inscription/',     views.VueInscription.as_view(),    name='inscription'),
    path('profil/<str:username>/', views.VueProfil.as_view(),   name='profil'),
    path('modifier-profil/', views.VueModifierProfil.as_view(), name='modifier_profil'),

    # ── Réinitialisation du mot de passe ──────────────────────────────────
    path('mot-de-passe-oublie/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/mot_de_passe_oublie.html',
             email_template_name='accounts/email_reinitialisation.html',
             subject_template_name='accounts/email_reinitialisation_sujet.txt',
             form_class=views.FormulaireMotDePasseOublie,
             success_url='/comptes/mot-de-passe-oublie/envoye/',
             extra_email_context={'site_name': 'Enoschofficiel'},
         ),
         name='mot_de_passe_oublie'),

    path('mot-de-passe-oublie/envoye/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/mot_de_passe_oublie_envoye.html'
         ),
         name='password_reset_done'),

    path('reinitialiser/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/reinitialiser_mot_de_passe.html',
             form_class=views.FormulaireNouveauMotDePasse,
             success_url='/comptes/reinitialiser/termine/',
         ),
         name='password_reset_confirm'),

    path('reinitialiser/termine/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/reinitialiser_mot_de_passe_termine.html'
         ),
         name='password_reset_complete'),
]