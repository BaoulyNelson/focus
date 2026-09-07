from django import forms
from django.utils import timezone
from django.utils.text import slugify
from .models import Article, Categorie, Tag

_INPUT  = 'form-control'
_SELECT = 'form-select'


class FormulaireArticle(forms.ModelForm):
    tags_input = forms.CharField(
        label='Tags',
        required=False,
        widget=forms.TextInput(attrs={
            'class': _INPUT,
            'placeholder': 'politique, economie, culture  (virgules)',
            'id': 'tags-input',
        }),
        help_text='Tags separes par des virgules'
    )

    class Meta:
        model  = Article
        fields = ['titre', 'categorie', 'extrait', 'contenu',
                  'image_principale', 'status', 'est_a_la_une', 'est_breaking']
        widgets = {
            'titre':     forms.TextInput(attrs={'class': _INPUT + ' form-control-lg',
                                                'placeholder': "Titre de l'article"}),
            'categorie': forms.Select(attrs={'class': _SELECT}),
            'extrait':   forms.Textarea(attrs={'class': _INPUT, 'rows': 3,
                                               'placeholder': 'Resume court (genere automatiquement si vide)'}),
            'image_principale': forms.FileInput(attrs={'class': _INPUT}),
            'status':    forms.Select(attrs={'class': _SELECT}),
            'est_a_la_une': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_breaking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'titre': 'Titre *', 'categorie': 'Categorie', 'extrait': 'Extrait / Resume',
            'contenu': 'Contenu *', 'image_principale': 'Image principale', 'status': 'Statut',
            'est_a_la_une': 'Mettre a la une', 'est_breaking': 'Breaking news',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags_input'].initial = ', '.join(
                t.nom for t in self.instance.tags.all()
            )

    def save(self, commit=True):
        article = super().save(commit=False)
        if self.user and not article.auteur_id:
            article.auteur = self.user
        if article.status == 'publie' and not article.published_at:
            article.published_at = timezone.now()
        if commit:
            article.save()
            article.tags.clear()
            raw = self.cleaned_data.get('tags_input', '')
            for name in [t.strip() for t in raw.split(',') if t.strip()]:
                tag, _ = Tag.objects.get_or_create(
                    slug=slugify(name), defaults={'nom': name}
                )
                article.tags.add(tag)
        return article


class FormulaireCategorieAdmin(forms.ModelForm):
    class Meta:
        model  = Categorie
        fields = ['nom', 'description', 'image', 'couleur', 'ordre']
        widgets = {
            'nom':         forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image':       forms.FileInput(attrs={'class': 'form-control'}),
            'couleur':     forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'ordre':       forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom': 'Nom de la categorie', 'description': 'Description',
            'image': 'Image', 'couleur': "Couleur d'accentuation",
            'ordre': "Ordre d'affichage",
        }
