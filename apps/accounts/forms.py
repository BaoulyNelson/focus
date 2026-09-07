from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

_INPUT   = 'form-control'
_SELECT  = 'form-select'
_CHECK   = 'form-check-input'
_FILE    = 'form-control'


class FormulaireConnexion(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur ou email",
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': "Nom d'utilisateur ou email", 'autofocus': True})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Mot de passe'})
    )
    error_messages = {
        'invalid_login': "Nom d'utilisateur ou mot de passe incorrect.",
        'inactive': 'Ce compte est desactive.',
    }


class FormulaireInscription(UserCreationForm):
    first_name = forms.CharField(label='Prenom', max_length=100,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Votre prenom'}))
    last_name  = forms.CharField(label='Nom', max_length=100,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Votre nom'}))
    email = forms.EmailField(label='Adresse email',
        widget=forms.EmailInput(attrs={'class': _INPUT, 'placeholder': 'votre@email.com'}))
    username = forms.CharField(label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'nom_utilisateur'}))
    password1 = forms.CharField(label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Choisissez un mot de passe'}))
    password2 = forms.CharField(label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Repetez le mot de passe'}))

    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Un compte avec cet email existe deja.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est deja pris.")
        return username


class FormulaireModificationProfil(forms.ModelForm):
    first_name = forms.CharField(label='Prenom', max_length=100,
        widget=forms.TextInput(attrs={'class': _INPUT}))
    last_name  = forms.CharField(label='Nom', max_length=100,
        widget=forms.TextInput(attrs={'class': _INPUT}))
    email = forms.EmailField(label='Email',
        widget=forms.EmailInput(attrs={'class': _INPUT}))

    class Meta:
        model  = UserProfile
        fields = ('bio', 'avatar', 'site_web', 'twitter')
        widgets = {
            'bio':      forms.Textarea(attrs={'class': _INPUT, 'rows': 4}),
            'avatar':   forms.FileInput(attrs={'class': _FILE}),
            'site_web': forms.URLInput(attrs={'class': _INPUT}),
            'twitter':  forms.TextInput(attrs={'class': _INPUT, 'placeholder': '@votre_twitter'}),
        }
        labels = {
            'bio': 'Biographie', 'avatar': 'Photo de profil',
            'site_web': 'Site web', 'twitter': 'Twitter',
        }
