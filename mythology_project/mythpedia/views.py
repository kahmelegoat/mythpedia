from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mythology, Character, FavoriteMythology, FavoriteCharacter, Suggestion 
# from .models import MythStory # Décommentez si vous utilisez MythStory
from .forms import SuggestionForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.core.mail import send_mail # <<< AJOUTÉ pour l'envoi d'email
from django.urls import reverse # <<< AJOUTÉ pour construire des URLs absolues pour l'email

@login_required
def mythology_list(request):
    all_mythologies = Mythology.objects.all().order_by('title')
    paginator = Paginator(all_mythologies, 8) 
    page_number = request.GET.get('page')
    try:
        mythologies_page = paginator.page(page_number)
    except PageNotAnInteger:
        mythologies_page = paginator.page(1)
    except EmptyPage:
        mythologies_page = paginator.page(paginator.num_pages)
    context = {
        'mythologies_page': mythologies_page,
        'page_title': 'Liste des Mythologies'
    }
    return render(request, 'mythpedia/mythology_list.html', context)

@login_required
def mythology_detail(request, mythology_slug):
    mythology = get_object_or_404(Mythology, slug=mythology_slug)
    characters = Character.objects.filter(mythology=mythology).order_by('name')
    # stories = mythology.stories.all().order_by('title') # Si vous utilisez le related_name 'stories' et le modèle MythStory
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteMythology.objects.filter(user=request.user, mythology=mythology).exists()
            
    context = {
        'mythology': mythology,
        'characters': characters,
        # 'stories': stories, # Décommentez si MythStory est actif
        'is_favorite': is_favorite,
        'page_title': mythology.title 
    }
    return render(request, 'mythpedia/mythology_detail.html', context)

@login_required
def character_detail(request, mythology_slug, character_slug):
    character = get_object_or_404(
        Character.objects.select_related('mythology'), 
        slug=character_slug, 
        mythology__slug=mythology_slug
    )
    is_favorite_character = False
    if request.user.is_authenticated:
        is_favorite_character = FavoriteCharacter.objects.filter(user=request.user, character=character).exists()
    # stories_featuring_character = character.featured_in_stories.all().order_by('title') # Si related_name 'featured_in_stories' et MythStory actif
    context = {
        'character': character,
        'mythology': character.mythology,
        'is_favorite_character': is_favorite_character,
        # 'stories_featuring_character': stories_featuring_character, # Décommentez si MythStory actif
        'page_title': character.name
    }
    return render(request, 'mythpedia/character_detail.html', context)

@login_required
def add_to_favorites(request, mythology_slug):
    mythology = get_object_or_404(Mythology, slug=mythology_slug)
    FavoriteMythology.objects.get_or_create(user=request.user, mythology=mythology)
    messages.success(request, f"'{mythology.title}' a été ajoutée à vos favoris.")
    return redirect('mythpedia:mythology_detail', mythology_slug=mythology_slug)

@login_required
def remove_from_favorites(request, mythology_slug):
    mythology = get_object_or_404(Mythology, slug=mythology_slug)
    favorite_entry = FavoriteMythology.objects.filter(user=request.user, mythology=mythology)
    if favorite_entry.exists():
        favorite_entry.delete()
        messages.success(request, f"'{mythology.title}' a été retirée de vos favoris.")
    else:
        messages.info(request, f"'{mythology.title}' n'était pas dans vos favoris.")
    return redirect('mythpedia:mythology_detail', mythology_slug=mythology_slug)

@login_required
def add_character_to_favorites(request, mythology_slug, character_slug):
    character = get_object_or_404(
        Character.objects.select_related('mythology'), 
        slug=character_slug, 
        mythology__slug=mythology_slug
    )
    FavoriteCharacter.objects.get_or_create(user=request.user, character=character)
    messages.success(request, f"'{character.name}' a été ajouté à vos personnages favoris.")
    return redirect('mythpedia:character_detail', mythology_slug=character.mythology.slug, character_slug=character.slug)

@login_required
def remove_character_from_favorites(request, mythology_slug, character_slug):
    character = get_object_or_404(
        Character.objects.select_related('mythology'), 
        slug=character_slug, 
        mythology__slug=mythology_slug
    )
    favorite_entry = FavoriteCharacter.objects.filter(user=request.user, character=character)
    if favorite_entry.exists():
        favorite_entry.delete()
        messages.success(request, f"'{character.name}' a été retiré de vos personnages favoris.")
    else:
        messages.info(request, f"'{character.name}' n'était pas dans vos personnages favoris.")
    return redirect('mythpedia:character_detail', mythology_slug=character.mythology.slug, character_slug=character.slug)

@login_required
def user_favorites_list(request):
    favorite_mythologies_entries = FavoriteMythology.objects.filter(user=request.user).select_related('mythology').order_by('-added_on')
    mythologies_in_favorites = [fav.mythology for fav in favorite_mythologies_entries]
    favorite_characters_entries = FavoriteCharacter.objects.filter(user=request.user).select_related('character', 'character__mythology').order_by('-added_on')
    characters_in_favorites = [fav.character for fav in favorite_characters_entries]
    context = {
        'favorite_mythologies': mythologies_in_favorites,
        'favorite_characters': characters_in_favorites,
        'page_title': 'Mes Favoris'
    }
    return render(request, 'mythpedia/user_favorites_list.html', context)

# --- VUE POUR LES SUGGESTIONS AVEC NOTIFICATION EMAIL ---
def submit_suggestion(request):
    form_kwargs = {}
    if request.user.is_authenticated:
        form_kwargs['user'] = request.user
        
    if request.method == 'POST':
        form = SuggestionForm(request.POST, **form_kwargs)
        if form.is_valid():
            suggestion = form.save(commit=False)
            if request.user.is_authenticated:
                suggestion.user = request.user
            suggestion.save()
            
            # --- Envoi de l'email de notification ---
            try:
                subject = f"Nouvelle Suggestion sur MythPedia: {suggestion.title[:50]}"
                user_info = suggestion.user.username if suggestion.user else suggestion.name_or_email or "Anonyme"
                
                # Construire l'URL absolue vers la suggestion dans l'admin
                # Note: admin:app_label_model_change ou admin:app_label_model_changelist
                try:
                    admin_url_path = reverse('admin:mythpedia_suggestion_change', args=[suggestion.id])
                    admin_url_full = request.build_absolute_uri(admin_url_path)
                except Exception: # Au cas où le reverse échoue pour une raison quelconque
                    admin_url_full = request.build_absolute_uri(f'/admin/mythpedia/suggestion/{suggestion.id}/change/')


                message_body = (
                    f"Une nouvelle suggestion a été soumise :\n\n"
                    f"Type: {suggestion.get_submission_type_display()}\n"
                    f"Titre: {suggestion.title}\n"
                    f"Soumis par: {user_info}\n\n"
                    f"Description:\n{suggestion.description}\n\n"
                    f"Voir dans l'admin : {admin_url_full}\n"
                )
                
                send_mail(
                    subject,
                    message_body,
                    settings.DEFAULT_FROM_EMAIL, # Votre adresse d'expéditeur configurée
                    [settings.ADMIN_EMAIL_FOR_SUGGESTIONS], # L'adresse admin configurée
                    fail_silently=False, # Mettre à True en production pour ne pas bloquer si l'email échoue
                )
                messages.success(request, "Merci ! Votre suggestion a été envoyée et sera examinée.")
            except Exception as e:
                # Loggez l'erreur d'email ici si vous avez un système de logging
                print(f"Erreur lors de l'envoi de l'email de notification de suggestion: {e}")
                messages.warning(request, "Votre suggestion a été enregistrée, mais une erreur est survenue lors de l'envoi de la notification à l'administrateur.")

            return redirect('mythpedia:mythology_list') 
        else:
            messages.error(request, "Il y a eu une erreur dans votre formulaire. Veuillez vérifier les champs et les messages ci-dessous.")
    else:
        form = SuggestionForm(**form_kwargs)
    context = {
        'form': form,
        'page_title': 'Suggérer du Contenu'
    }
    return render(request, 'mythpedia/submit_suggestion.html', context)

# --- Vues d'Authentification ---
def register_request(request):
    if request.user.is_authenticated:
        return redirect('mythpedia:mythology_list')
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue.")
            return redirect('mythpedia:mythology_list')
        else:
            for field_name, error_list in form.errors.as_data().items():
                for error in error_list:
                    field_label = form.fields[field_name].label if field_name != '__all__' and field_name in form.fields else ''
                    messages.error(request, f"{field_label or 'Erreur Générale'}: {error.message}")
    else:
        form = UserCreationForm()
    return render(request, "mythpedia/register.html", {"register_form": form, "page_title": "Inscription"})

def login_request(request):
    if request.user.is_authenticated:
        next_page = request.GET.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(settings.LOGIN_REDIRECT_URL) 
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Vous êtes maintenant connecté en tant que {username}.")
                next_page_from_form = request.POST.get('next', '')
                next_page_from_get = request.GET.get('next', '')
                next_page = next_page_from_form or next_page_from_get
                if next_page:
                    return redirect(next_page)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
        else:
            for field_name, error_list in form.errors.as_data().items():
                for error in error_list:
                    field_label = form.fields[field_name].label if field_name != '__all__' and field_name in form.fields else 'Erreur'
                    messages.error(request, f"{field_label or 'Erreur Générale'}: {error.message}")
            if not form.errors.items():
                 messages.error(request,"Nom d'utilisateur ou mot de passe invalide (vérification générale).")
    else:
        form = AuthenticationForm()
    return render(request, "mythpedia/login.html", {"login_form": form, "page_title": "Connexion", "next_page": request.GET.get('next', '')})

def logout_request(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect(settings.LOGOUT_REDIRECT_URL)