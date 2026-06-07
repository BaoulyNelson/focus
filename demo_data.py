"""
Script de données de démonstration — LeMédia
============================================
Place ce fichier dans le dossier racine du projet (à côté de manage.py)
puis lance :  python demo_data.py

Il crée :
  - 1 superutilisateur  (admin / admin1234)
  - 3 utilisateurs      (auteur, editeur, lecteur)
  - 6 catégories
  - 12 tags
  - 20 articles réalistes (avec statuts variés, images placeholder)
  - 15 commentaires + réponses
  - 5 messages de contact
"""

import os
import sys
import django
from pathlib import Path

# ── Bootstrap Django ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "focus.settings")
django.setup()

# ── Imports après setup ───────────────────────────────────────────────────────
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from apps.accounts.models import UserProfile
from apps.articles.models import Article, Categorie, Tag
from apps.comments.models import Commentaire
from apps.contact.models import MessageContact

# ══════════════════════════════════════════════════════════════════════════════
# Utilitaires
# ══════════════════════════════════════════════════════════════════════════════

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"

def ok(msg):  print(f"  {GREEN}✓{RESET} {msg}")
def info(msg):print(f"  {CYAN}→{RESET} {msg}")
def warn(msg):print(f"  {YELLOW}!{RESET} {msg}")
def title(msg):print(f"\n{BOLD}{CYAN}{'━'*55}{RESET}\n{BOLD}  {msg}{RESET}\n{'━'*55}")

def creer_user(username, password, first_name, last_name, email, role, is_staff=False):
    user, created = User.objects.get_or_create(username=username, defaults={
        "first_name": first_name, "last_name": last_name,
        "email": email, "is_staff": is_staff,
    })
    if created:
        user.set_password(password)
        user.save()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.bio  = f"{first_name} {last_name} – rédacteur pour LeMédia."
    profile.save()
    return user, created


# ══════════════════════════════════════════════════════════════════════════════
# 1. UTILISATEURS
# ══════════════════════════════════════════════════════════════════════════════
title("1. Création des utilisateurs")

admin, c = creer_user("admin", "admin1234", "Admin", "LeMédia",
                       "admin@lemedia.ht", "editeur", is_staff=True)
admin.is_superuser = True; admin.save()
ok(f"Superutilisateur : admin / admin1234  {'(nouveau)' if c else '(existant)'}")

auteur, c = creer_user("marie_journaliste", "Demo1234!", "Marie", "Joseph",
                        "marie@lemedia.ht", "auteur")
ok(f"Auteur           : marie_journaliste / Demo1234!  {'(nouveau)' if c else '(existant)'}")

editeur, c = creer_user("jean_editeur", "Demo1234!", "Jean", "Pierre",
                         "jean@lemedia.ht", "editeur")
ok(f"Éditeur          : jean_editeur / Demo1234!  {'(nouveau)' if c else '(existant)'}")

lecteur, c = creer_user("paul_lecteur", "Demo1234!", "Paul", "Dumont",
                          "paul@lemedia.ht", "lecteur")
ok(f"Lecteur          : paul_lecteur / Demo1234!  {'(nouveau)' if c else '(existant)'}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. CATÉGORIES
# ══════════════════════════════════════════════════════════════════════════════
title("2. Création des catégories")

CATEGORIES = [
    ("Politique",     "#e63946", "Actualité politique nationale et internationale", 1),
    ("Économie",      "#2196F3", "Finances, marchés, développement économique",     2),
    ("Société",       "#4CAF50", "Faits de société, culture et mode de vie",        3),
    ("Sport",         "#FF9800", "Football, athlétisme et toutes disciplines",       4),
    ("International", "#9C27B0", "Actualité internationale et diplomatie",           5),
    ("Technologie",   "#00BCD4", "Numérique, innovation et sciences",               6),
]

cats = {}
for nom, couleur, desc, ordre in CATEGORIES:
    cat, created = Categorie.objects.get_or_create(
        slug=slugify(nom),
        defaults={"nom": nom, "couleur": couleur, "description": desc, "ordre": ordre}
    )
    cats[nom] = cat
    ok(f"{nom:15s}  {couleur}  {'créée' if created else 'existante'}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. TAGS
# ══════════════════════════════════════════════════════════════════════════════
title("3. Création des tags")

TAG_NAMES = [
    "haïti", "caraïbes", "développement", "jeunesse", "éducation",
    "élections", "football", "diaspora", "agriculture", "santé",
    "innovation", "climat",
]
tags = {}
for name in TAG_NAMES:
    tag, _ = Tag.objects.get_or_create(slug=slugify(name), defaults={"nom": name})
    tags[name] = tag
ok(f"{len(tags)} tags créés / vérifiés")


# ══════════════════════════════════════════════════════════════════════════════
# 4. ARTICLES
# ══════════════════════════════════════════════════════════════════════════════
title("4. Création des articles")

now = timezone.now()

ARTICLES = [
    # (titre, catégorie, auteur, statut, a_la_une, breaking, jours_ago, tags_list, contenu_court)
    (
        "Le gouvernement annonce un plan d'urgence pour relancer l'économie nationale",
        "Politique", admin, "publie", True, True, 0,
        ["haïti", "développement", "élections"],
        """<p>Le Premier ministre a présenté hier un ambitieux plan de relance économique visant à stimuler la croissance dans un contexte de crise prolongée. Ce programme, doté d'une enveloppe de plusieurs milliards de gourdes, ciblera en priorité les secteurs agricole, industriel et touristique.</p>
<h2>Les grandes lignes du plan</h2>
<p>Le gouvernement prévoit notamment la création de <strong>50 000 emplois directs</strong> dans les 18 prochains mois, ainsi qu'un soutien renforcé aux petites et moyennes entreprises. Des zones franches supplémentaires seront établies dans le Nord et l'Artibonite pour attirer les investisseurs étrangers.</p>
<blockquote>« Nous avons la responsabilité de redonner espoir à notre population. Ce plan est un premier pas vers une Haïti plus prospère. »</blockquote>
<p>L'opposition a accueilli ces annonces avec prudence, réclamant des détails concrets sur le financement et les mécanismes de contrôle. La société civile, quant à elle, appelle à une large consultation avant la mise en œuvre.</p>
<h2>Réactions des partenaires internationaux</h2>
<p>La communauté internationale a salué l'initiative, conditionnant toutefois son soutien à des réformes structurelles et à une plus grande transparence dans la gestion des fonds publics.</p>"""
    ),
    (
        "La Sélection Nationale qualifiée pour la Gold Cup 2025",
        "Sport", auteur, "publie", True, False, 1,
        ["haïti", "football", "caraïbes"],
        """<p>Les Grenadiers ont décroché leur ticket pour la Gold Cup 2025 après une victoire éclatante face à Trinidad-et-Tobago (2-0) lors du match décisif disputé au Stade Sylvio Cator.</p>
<h2>Un match historique</h2>
<p>Devant un public en ferveur, les joueurs haïtiens ont livré une prestation de haute qualité. Le capitaine a ouvert le score à la 34e minute d'une frappe puissante, avant qu'un deuxième but en seconde période ne scelle la qualification.</p>
<p>Le sélectionneur national a salué la <strong>détermination exceptionnelle</strong> de ses joueurs qui ont su gérer la pression tout au long de la rencontre.</p>
<blockquote>« Ce résultat est le fruit de mois de travail acharné. Nous allons préparer la Gold Cup avec la même rigueur. »</blockquote>
<h2>Les prochaines étapes</h2>
<p>Le tirage au sort de la compétition aura lieu le mois prochain. L'équipe entrera en stage de préparation dès la semaine prochaine avec plusieurs joueurs évoluant en Europe rappelés pour l'occasion.</p>"""
    ),
    (
        "Inauguration du nouveau centre technologique de Port-au-Prince",
        "Technologie", editeur, "publie", True, False, 2,
        ["haïti", "innovation", "jeunesse"],
        """<p>Un nouveau hub technologique a officiellement ouvert ses portes dans la capitale haïtienne, offrant aux jeunes entrepreneurs un espace de travail collaboratif équipé des dernières technologies.</p>
<h2>Un espace dédié à l'innovation</h2>
<p>Ce centre de 2 000 mètres carrés dispose de <strong>salles de formation</strong>, d'espaces de coworking, d'un fablab et d'une salle de conférence haute technologie. Il est conçu pour accueillir jusqu'à 300 membres simultanément.</p>
<p>Le projet, financé par un consortium d'investisseurs privés et de partenaires internationaux, ambitionne de faire d'Haïti un acteur du numérique dans la région caribéenne.</p>
<blockquote>« La technologie est le levier qui permettra à notre jeunesse de construire le pays de demain. »</blockquote>"""
    ),
    (
        "Crise climatique : les agriculteurs haïtiens face à la sécheresse",
        "Société", auteur, "publie", False, False, 3,
        ["haïti", "agriculture", "climat"],
        """<p>Les pluies tardives et insuffisantes de cette saison ont plongé plusieurs départements dans une situation agricole critique. Les paysans de l'Artibonite et du Nord-Ouest tirent la sonnette d'alarme.</p>
<h2>Des récoltes compromises</h2>
<p>Selon les premières estimations du ministère de l'Agriculture, <strong>près de 40% des cultures</strong> de maïs et de haricots sont menacées dans les zones les plus touchées. Les prix alimentaires dans les marchés locaux ont déjà commencé à grimper.</p>
<p>Les organisations paysannes réclament un plan d'urgence incluant la distribution de semences résistantes à la sécheresse et la mise en place de systèmes d'irrigation temporaires.</p>"""
    ),
    (
        "La diaspora haïtienne investit massivement dans l'immobilier local",
        "Économie", editeur, "publie", False, False, 4,
        ["haïti", "diaspora", "développement"],
        """<p>Les transferts de fonds de la diaspora représentent désormais plus de 20% du PIB haïtien. Une partie croissante de cet argent est désormais dirigée vers l'immobilier résidentiel et commercial.</p>
<h2>Un boom immobilier inédit</h2>
<p>Les villes de Pétion-Ville, Delmas et Tabarre connaissent une effervescence constructive sans précédent. Les promoteurs immobiliers rapportent une hausse de <strong>35% des transactions</strong> en un an, portée en grande partie par des acheteurs basés à Miami, New York et Montréal.</p>"""
    ),
    (
        "Réforme du système éducatif : ce qui va changer dès septembre",
        "Société", auteur, "publie", False, False, 5,
        ["haïti", "éducation", "jeunesse"],
        """<p>Le ministère de l'Éducation nationale a dévoilé les grands axes de sa réforme qui entrera en vigueur à la rentrée prochaine. Nouveaux programmes, formation des enseignants et numérique sont au cœur du dispositif.</p>
<h2>Nouveaux programmes scolaires</h2>
<p>Les curricula du primaire et du secondaire ont été entièrement repensés pour intégrer davantage de compétences pratiques, de pensée critique et de notions numériques. L'enseignement bilingue créole-français sera renforcé dans toutes les écoles publiques.</p>"""
    ),
    (
        "Sommet caribéen : Haïti signe trois accords commerciaux majeurs",
        "International", admin, "publie", False, False, 6,
        ["haïti", "caraïbes", "développement"],
        """<p>En marge du sommet de la CARICOM, Haïti a signé trois accords commerciaux avec la Jamaïque, Trinidad-et-Tobago et les Bahamas. Ces partenariats ouvrent de nouvelles perspectives pour les exportations haïtiennes.</p>
<h2>Des opportunités pour les exportateurs</h2>
<p>Les accords portent notamment sur l'élimination progressive des droits de douane sur les produits agricoles, les textiles et l'artisanat haïtiens. Les entreprises locales exportatrices accueilleront favorablement ces mesures qui leur ouvrent des marchés supplémentaires.</p>"""
    ),
    (
        "Santé publique : vaccination contre la malaria dans l'Artibonite",
        "Société", auteur, "publie", False, False, 7,
        ["haïti", "santé"],
        """<p>Le ministère de la Santé publique a lancé une vaste campagne de vaccination contre la malaria dans le département de l'Artibonite, l'une des zones les plus touchées du pays.</p>
<h2>Une campagne d'envergure</h2>
<p>En partenariat avec l'OMS et Médecins sans Frontières, cette campagne vise à vacciner <strong>200 000 personnes</strong> en trois mois. Des équipes mobiles sillonnent les communes les plus reculées pour atteindre les populations vulnérables.</p>"""
    ),
    (
        "Le port de Cap-Haïtien modernisé pour booster le commerce du Nord",
        "Économie", editeur, "publie", False, False, 8,
        ["haïti", "développement"],
        """<p>Des travaux d'agrandissement et de modernisation du port de Cap-Haïtien ont débuté cette semaine. Le chantier, d'une durée de 18 mois, permettra de tripler la capacité d'accueil des conteneurs.</p>
<h2>Un investissement stratégique</h2>
<p>Ce projet représente un investissement de 120 millions de dollars financés conjointement par l'État haïtien, la Banque interaméricaine de développement et des fonds privés. À terme, le port du Cap sera l'un des plus modernes de la Caraïbe.</p>"""
    ),
    (
        "Festival de Jacmel : un succès retentissant pour le tourisme culturel",
        "Société", auteur, "publie", False, False, 9,
        ["haïti", "caraïbes"],
        """<p>Le festival annuel des arts de Jacmel a rassemblé cette année plus de 15 000 visiteurs venus du monde entier. Un record qui confirme le potentiel touristique de la cité des arts.</p>
<h2>Cinq jours de créativité</h2>
<p>Expositions, performances de rue, ateliers d'artisanat et concerts ont animé la ville pendant cinq jours. Des artistes venus de France, du Canada, du Brésil et des États-Unis ont participé à cet événement devenu incontournable dans la région.</p>"""
    ),
    (
        "Élections municipales : le calendrier officiel enfin publié",
        "Politique", admin, "publie", False, True, 10,
        ["haïti", "élections"],
        """<p>Le Conseil Électoral Provisoire a rendu public le calendrier officiel des élections municipales. Le premier tour est fixé au troisième trimestre de l'année en cours.</p>
<h2>Un processus scruté de près</h2>
<p>Plusieurs partis politiques ont salué cette annonce tout en insistant sur la nécessité de garantir la sécurité des électeurs et des candidats. Des observateurs internationaux seront déployés dans tous les départements.</p>"""
    ),
    (
        "Haïti : une startup remporte le prix régional d'innovation numérique",
        "Technologie", auteur, "publie", False, False, 11,
        ["haïti", "innovation", "jeunesse"],
        """<p>La startup haïtienne PayEasy a remporté le Grand Prix de l'Innovation Numérique des Caraïbes pour sa solution de paiement mobile destinée aux zones rurales sans accès bancaire.</p>
<h2>Une solution locale à un problème local</h2>
<p>PayEasy permet aux populations rurales d'effectuer des transactions financières via un simple téléphone basique, sans internet, en utilisant la technologie USSD. La startup compte déjà 50 000 utilisateurs actifs dans trois départements.</p>"""
    ),
    (
        "Inondations dans le Sud : état des dégâts et plan d'aide d'urgence",
        "Société", editeur, "publie", False, True, 0,
        ["haïti", "climat"],
        """<p>Les fortes pluies des derniers jours ont provoqué des inondations dans plusieurs communes du département du Sud. Les autorités ont déclenché le plan d'urgence national.</p>
<h2>Bilan provisoire</h2>
<p>Les premières estimations font état de <strong>plusieurs milliers de familles sinistrées</strong>, de routes coupées et de ponts endommagés. La Protection Civile coordonne les opérations de secours avec l'appui des forces armées.</p>"""
    ),
    (
        "Interview exclusive : le sélectionneur national parle de l'avenir des Grenadiers",
        "Sport", auteur, "publie", False, False, 12,
        ["haïti", "football"],
        """<p>Rencontré en exclusivité par LeMédia, le sélectionneur de l'équipe nationale de football revient sur la qualification pour la Gold Cup et dévoile ses ambitions pour les prochaines années.</p>
<h2>Un projet ambitieux</h2>
<p>« Mon objectif est de qualifier Haïti pour la prochaine Coupe du Monde. Nous avons les talents, nous avons les joueurs. Il nous faut maintenant de la stabilité institutionnelle et des infrastructures adaptées. »</p>"""
    ),
    (
        "Réforme fiscale : les PME haïtiennes entre espoir et inquiétude",
        "Économie", editeur, "publie", False, False, 13,
        ["haïti", "développement"],
        """<p>Le projet de réforme fiscale soumis au Parlement prévoit d'alléger la charge des petites entreprises tout en élargissant l'assiette fiscale aux grandes sociétés. Les avis sont partagés.</p>
<h2>Ce que prévoit la réforme</h2>
<p>Les PME dont le chiffre d'affaires annuel est inférieur à 5 millions de gourdes bénéficieraient d'une exonération totale pendant les trois premières années d'existence. Un dispositif d'accompagnement fiscal gratuit serait également mis en place.</p>"""
    ),
    # Brouillons / en révision
    (
        "Enquête : l'état des routes nationales en 2025",
        "Société", auteur, "brouillon", False, False, 0,
        ["haïti"],
        "<p>Enquête en cours sur l'état des infrastructures routières. Article à paraître prochainement.</p>"
    ),
    (
        "Portrait : Marie Carmel, première femme ingénieure en chef au MTPTC",
        "Société", auteur, "en_revision", False, False, 0,
        ["haïti", "jeunesse"],
        "<p>Portrait inspirant d'une pionnière de l'ingénierie haïtienne. En cours de révision.</p>"
    ),
    (
        "Analyse : les enjeux économiques des prochaines élections",
        "Politique", editeur, "brouillon", False, False, 0,
        ["haïti", "élections", "développement"],
        "<p>Analyse approfondie en préparation. Publication prévue avant le scrutin.</p>"
    ),
    (
        "Tourisme spatial : et si Haïti misait sur le tourisme de luxe ?",
        "Économie", auteur, "brouillon", False, False, 0,
        ["caraïbes", "développement"],
        "<p>Réflexion sur de nouvelles niches touristiques pour l'économie haïtienne.</p>"
    ),
    (
        "Technologie agricole : des drones au service des paysans haïtiens",
        "Technologie", editeur, "en_revision", False, False, 0,
        ["haïti", "agriculture", "innovation"],
        "<p>Comment les nouvelles technologies peuvent transformer l'agriculture haïtienne. Article en révision éditoriale.</p>"
    ),
]

count = 0
for (titre, cat_nom, auteur_obj, statut, une, breaking,
     jours, tag_list, contenu) in ARTICLES:
    slug = slugify(titre)
    if Article.objects.filter(slug=slug).exists():
        warn(f"Existe déjà : {titre[:55]}")
        continue
    pub_date = now - timezone.timedelta(days=jours) if statut == "publie" else None
    art = Article.objects.create(
        titre=titre,
        slug=slug,
        contenu=contenu,
        auteur=auteur_obj,
        categorie=cats.get(cat_nom),
        status=statut,
        est_a_la_une=une,
        est_breaking=breaking,
        published_at=pub_date,
        nombre_vues=__import__('random').randint(50, 4500) if statut == "publie" else 0,
    )
    for t in tag_list:
        if t in tags:
            art.tags.add(tags[t])
    count += 1
    badge = ""
    if une:     badge += " ⭐une"
    if breaking:badge += " 🔴breaking"
    ok(f"[{statut:10s}] {titre[:52]}{badge}")

info(f"{count} articles créés")


# ══════════════════════════════════════════════════════════════════════════════
# 5. COMMENTAIRES
# ══════════════════════════════════════════════════════════════════════════════
title("5. Création des commentaires")

publies = list(Article.objects.filter(status="publie")[:6])
users   = [admin, auteur, editeur, lecteur]

COMMENTAIRES = [
    "Excellent article, très bien documenté. Merci à la rédaction !",
    "Je partage entièrement cette analyse. Il est grand temps que les autorités agissent.",
    "Des informations importantes pour notre pays. Continuez ce bon travail !",
    "Très intéressant. J'aurais aimé avoir plus de détails sur les chiffres cités.",
    "Article bien écrit mais je suis en désaccord avec certaines conclusions.",
    "Merci pour cet éclairage. La situation est vraiment préoccupante.",
    "Enfin un média qui traite de ce sujet sérieusement !",
    "Je suis journaliste et je confirme ces informations. Bonne couverture.",
    "Partagé sur mes réseaux. Tous les Haïtiens devraient lire ça.",
    "Des questions importantes sont soulevées ici. Espérons que le gouvernement réponde.",
]

REPONSES = [
    "Tout à fait d'accord avec votre commentaire !",
    "Merci pour votre contribution à la discussion.",
    "Je nuancerais votre point de vue, mais je comprends votre argument.",
    "Excellente remarque. La rédaction a bien fait de publier cet article.",
]

import random
cpt = 0
for i, art in enumerate(publies):
    # 2-3 commentaires par article
    for j in range(random.randint(2, 3)):
        user = users[(i + j) % len(users)]
        c = Commentaire.objects.create(
            article=art,
            auteur=user,
            contenu=COMMENTAIRES[(i * 3 + j) % len(COMMENTAIRES)],
            is_approved=True,
            created_at=now - timezone.timedelta(hours=random.randint(1, 72)),
        )
        cpt += 1
        # Réponse à certains commentaires
        if j == 0 and i < 3:
            rep_user = users[(i + j + 1) % len(users)]
            Commentaire.objects.create(
                article=art,
                auteur=rep_user,
                contenu=REPONSES[i % len(REPONSES)],
                parent=c,
                is_approved=True,
                created_at=now - timezone.timedelta(hours=random.randint(1, 24)),
            )
            cpt += 1

ok(f"{cpt} commentaires créés")


# ══════════════════════════════════════════════════════════════════════════════
# 6. MESSAGES DE CONTACT
# ══════════════════════════════════════════════════════════════════════════════
title("6. Création des messages de contact")

MESSAGES = [
    ("Sophie Marceau",    "sophie@gmail.com",       "redaction",   "Bonjour, je souhaite proposer un reportage sur la situation des femmes entrepreneures en Haïti. Serait-il possible d'en discuter avec votre équipe ?"),
    ("Marc Antoine",      "marc.antoine@yahoo.com", "correction",  "Dans votre article sur les élections, il y a une erreur de date. Le scrutin est prévu en juillet et non en juin comme indiqué. Merci de corriger."),
    ("Entreprise XY",     "contact@entreprise.ht",  "publicite",   "Notre groupe est intéressé par des opportunités publicitaires sur votre plateforme. Pourriez-vous nous envoyer votre grille tarifaire ?"),
    ("Citoyen Anonyme",   "citoyen@proton.me",      "general",     "Félicitations pour la qualité de votre couverture journalistique. LeMédia est devenu ma référence pour l'information en Haïti. Continuez ainsi !"),
    ("ONG Haïti Demain",  "info@haitidemain.org",   "partenariat", "Notre organisation souhaite explorer un partenariat médiatique pour la couverture de nos projets de développement. Serait-il possible d'organiser une réunion ?"),
]

for nom, email, sujet, message in MESSAGES:
    if not MessageContact.objects.filter(email=email).exists():
        MessageContact.objects.create(
            nom=nom, email=email, sujet=sujet, message=message,
            is_read=random.choice([True, False]),
        )
        ok(f"{nom:22s} [{sujet}]")
    else:
        warn(f"{nom} — déjà existant")


# ══════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ══════════════════════════════════════════════════════════════════════════════
title("Résumé de la démonstration")

pub  = Article.objects.filter(status="publie").count()
brou = Article.objects.filter(status="brouillon").count()
rev  = Article.objects.filter(status="en_revision").count()

print(f"""
  {BOLD}Utilisateurs{RESET}
    ├── admin             /  admin1234        (superuser)
    ├── marie_journaliste /  Demo1234!        (auteur)
    ├── jean_editeur      /  Demo1234!        (éditeur)
    └── paul_lecteur      /  Demo1234!        (lecteur)

  {BOLD}Contenu créé{RESET}
    ├── Catégories  : {Categorie.objects.count()}
    ├── Tags        : {Tag.objects.count()}
    ├── Articles    : {Article.objects.count()} total  ({pub} publiés · {brou} brouillons · {rev} en révision)
    ├── Commentaires: {Commentaire.objects.count()}
    └── Messages    : {MessageContact.objects.count()}

  {BOLD}URLs à tester{RESET}
    ├── http://127.0.0.1:8000/                     ← Accueil
    ├── http://127.0.0.1:8000/actualites/           ← Liste articles
    ├── http://127.0.0.1:8000/categorie/politique/  ← Catégorie
    ├── http://127.0.0.1:8000/recherche/?q=haiti    ← Recherche
    ├── http://127.0.0.1:8000/contact/              ← Contact
    ├── http://127.0.0.1:8000/comptes/connexion/    ← Connexion
    ├── http://127.0.0.1:8000/tableau-de-bord/      ← Dashboard
    └── http://127.0.0.1:8000/administration/       ← Admin Django

{GREEN}{BOLD}  Données de démonstration chargées avec succès !{RESET}
""")
