from django.conf import settings
from django.core.cache import cache
from .models import Categorie, Article, Configuration


def site_context(request):
    config = Configuration.get()

    categories = cache.get('nav_categories')
    if not categories:
        categories = list(Categorie.objects.all()[:8])
        cache.set('nav_categories', categories, 300)

    breaking = cache.get('breaking_news')
    if not breaking:
        breaking = list(
            Article.objects.filter(status='publie', est_breaking=True)
                           .order_by('-published_at')[:5]
        )
        cache.set('breaking_news', breaking, 60)

    return {
        'SITE_NAME':        config.site_name,
        'SITE_DESCRIPTION': config.site_description,
        'SITE_TAGLINE':     config.site_tagline,
        'CONTACT_EMAIL':    config.contact_email,
        'site_config':      config,
        'nav_categories':   categories,
        'breaking_news':    breaking,
    }