# mythology_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mythpedia import views as mythpedia_views # Importer les vues de mythpedia

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mythpedia_views.login_request, name='home_login'), # La racine pointe vers la vue de connexion
    path('mythpedia/', include('mythpedia.urls')), # Garder les autres URLs de mythpedia sous un préfixe
                                                # ou les définir individuellement ici si vous préférez.
                                                # Pour l'instant, on les laisse sous /mythpedia/
                                                # SAUF pour login, register, logout qui seront aussi à la racine.

    # Déplacer les URLs d'authentification à la racine aussi pour un accès plus direct
    path('register/', mythpedia_views.register_request, name='register'),
    path('login/', mythpedia_views.login_request, name='login'), # Répété mais name='login' est important pour LOGIN_URL
    path('logout/', mythpedia_views.logout_request, name='logout'),
]

# Pour servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)