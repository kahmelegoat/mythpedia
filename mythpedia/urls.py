from django.urls import path
from . import views

app_name = 'mythpedia'  # <<< AJOUTÉ : TRÈS IMPORTANT POUR LE NAMESPACING

# Le nom 'urlpatterns' est important pour que include() fonctionne.
urlpatterns = [
    # La racine de '/mythpedia/' sera la liste des mythologies.
    path('', views.mythology_list, name='mythology_list'),
    path('mythology/<slug:mythology_slug>/', views.mythology_detail, name='mythology_detail'),
    path('mythology/<slug:mythology_slug>/character/<slug:character_slug>/', views.character_detail, name='character_detail'),

    # URLs pour la gestion des favoris de Mythologies
    path('mythology/<slug:mythology_slug>/add_favorite/', views.add_to_favorites, name='add_to_favorites'),
    path('mythology/<slug:mythology_slug>/remove_favorite/', views.remove_from_favorites, name='remove_from_favorites'),
    
    # URLs pour les favoris de Personnages
    # Utilisation de mythology_slug et character_slug pour identifier le personnage de manière unique
    path('character/<slug:mythology_slug>/<slug:character_slug>/add_favorite/', views.add_character_to_favorites, name='add_character_to_favorites'),
    path('character/<slug:mythology_slug>/<slug:character_slug>/remove_favorite/', views.remove_character_from_favorites, name='remove_character_from_favorites'),

    # URL pour lister les favoris (mythologies et personnages)
    path('my-favorites/', views.user_favorites_list, name='user_favorites_list'),

    # URL pour la page de suggestions
    path('suggest/', views.submit_suggestion, name='submit_suggestion'),

    path('mythology/<slug:mythology_slug>/', views.mythology_detail, name='mythology_detail'),

    # Les URLs d'authentification sont supposées être gérées dans le urls.py principal du projet
    # pour être à la racine du site. Si vous les voulez sous /mythpedia/, décommentez-les.
    # path('register/', views.register_request, name='register'),
    # path('login/', views.login_request, name='login'),
    # path('logout/', views.logout_request, name='logout'),
]

# LES LIGNES SUIVANTES ÉTAIENT DES DOUBLONS ET ONT ÉTÉ SUPPRIMÉES :
# path('mythology/<slug:mythology_slug>/add_favorite/', views.add_to_favorites, name='add_favorite'),
# path('mythology/<slug:mythology_slug>/remove_favorite/', views.remove_from_favorites, name='remove_favorite'),
# path('my-favorites/', views.user_favorites_list, name='user_favorites_list'),

# CETTE LISTE urlpatterns ÉTAIT INCOMPLÈTE ET REDONDANTE, SUPPRIMÉE :
# urlpatterns = [
# # ... (vos URLs existantes) ...
# path('mythology/<slug:mythology_slug>/story/<slug:story_slug>/', views.mythstory_detail, name='mythstory_detail'),
# # ... (vos URLs de favoris et d'authentification si elles sont ici) ... 
# ]