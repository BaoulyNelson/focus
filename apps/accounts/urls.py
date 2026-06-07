from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('connexion/',       views.VueConnexion.as_view(),      name='connexion'),
    path('deconnexion/',     views.VueDeconnexion.as_view(),    name='deconnexion'),
    path('inscription/',     views.VueInscription.as_view(),    name='inscription'),
    path('profil/<str:username>/', views.VueProfil.as_view(),   name='profil'),
    path('modifier-profil/', views.VueModifierProfil.as_view(), name='modifier_profil'),
]
