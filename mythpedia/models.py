# mythpedia/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User 

# 1. DÉFINIR Mythology EN PREMIER
class Mythology(models.Model):
    title = models.CharField(max_length=100, verbose_name="Titre de la Mythologie")
    slug = models.SlugField(max_length=110, unique=True, blank=True, help_text="Identifiant URL (auto-généré à partir du titre si laissé vide)")
    icon_class = models.CharField(max_length=50, help_text="Classe Font Awesome (ex: 'fa-dragon')")
    color_from = models.CharField(max_length=50, help_text="Classe Tailwind pour début gradient (ex: 'from-red-500')")
    color_to = models.CharField(max_length=50, help_text="Classe Tailwind pour fin gradient (ex: 'to-yellow-400')")
    description = models.TextField(verbose_name="Description Complète")
    card_summary = models.CharField(max_length=200, blank=True, null=True, help_text="Texte court pour la carte principale (optionnel)")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            queryset = Mythology.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            while queryset.exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
                queryset = Mythology.objects.filter(slug=self.slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Mythologie"
        verbose_name_plural = "Mythologies"
        ordering = ['title']

# 2. DÉFINIR Character APRÈS Mythology (car il utilise Mythology)
class Character(models.Model):
    mythology = models.ForeignKey(Mythology, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=100, verbose_name="Nom du Personnage")
    slug = models.SlugField(max_length=110, blank=True, help_text="Identifiant URL (auto-généré, unique par mythologie)")
    role = models.CharField(max_length=150, verbose_name="Rôle principal", blank=True)
    description = models.TextField(verbose_name="Description du Personnage", blank=True)
    image_url = models.URLField(max_length=300, blank=True, null=True, help_text="URL de l'image du personnage (ex: Imgur)")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            queryset = Character.objects.filter(mythology=self.mythology, slug=unique_slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            while queryset.exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
                queryset = Character.objects.filter(mythology=self.mythology, slug=unique_slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.mythology.title})"

    class Meta:
        verbose_name = "Personnage"
        verbose_name_plural = "Personnages"
        ordering = ['mythology', 'name']
        unique_together = ('mythology', 'slug')

# 3. DÉFINIR FavoriteMythology APRÈS User et Mythology
class FavoriteMythology(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_mythologies')
    mythology = models.ForeignKey(Mythology, on_delete=models.CASCADE, related_name='favorited_by_users')
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'mythology')
        ordering = ['-added_on']
        verbose_name = "Mythologie Favorite" # Ajout pour l'admin
        verbose_name_plural = "Mythologies Favorites" # Ajout pour l'admin

    def __str__(self):
        return f"{self.user.username} favorites {self.mythology.title}"
    
# 4. DÉFINIR FavoriteCharacter APRÈS User et Character
class FavoriteCharacter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_characters')
    # Correction du related_name pour éviter conflit potentiel si Character a un autre M2M nommé 'favorited_by_users'
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='favorited_by_user_set') # ou 'character_favorites'
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'character')
        ordering = ['-added_on']
        verbose_name = "Personnage Favori"
        verbose_name_plural = "Personnages Favoris"

    def __str__(self):
        return f"{self.user.username} favorites {self.character.name}"

# 5. DÉFINIR Suggestion APRÈS User, Mythology, Character
class Suggestion(models.Model):
    SUBMISSION_TYPES = [
        ('MYTHOLOGY', 'Nouvelle Mythologie'),
        ('CHARACTER', 'Nouveau Personnage'),
        # ('STORY', 'Nouveau Mythe/Histoire'), # Commenté car MythStory n'est pas défini ici
        ('CORRECTION', 'Correction/Ajout d\'Information'),
        ('OTHER', 'Autre Suggestion'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('REVIEWED', 'En cours d\'examen'),
        ('APPROVED', 'Approuvée'),
        ('IMPLEMENTED', 'Implémentée'),
        ('REJECTED', 'Rejetée'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='suggestions_made', verbose_name="Utilisateur (si connecté)")
    name_or_email = models.CharField(max_length=150, blank=True, help_text="Votre nom ou email (si non connecté ou pour contact)")

    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPES, verbose_name="Type de Suggestion")
    title = models.CharField(max_length=200, verbose_name="Titre/Sujet de la Suggestion", help_text="Ex: 'Ajouter la Mythologie Sumérienne' ou 'Correction sur Zeus'")
    description = models.TextField(verbose_name="Détails de la Suggestion")
    
    related_mythology = models.ForeignKey(Mythology, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_suggestions_myth', verbose_name="Mythologie Concernée (si applicable)")
    related_character = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_suggestions_char', verbose_name="Personnage Concerné (si applicable)")
    # related_story = models.ForeignKey('MythStory', on_delete=models.SET_NULL, null=True, blank=True, related_name='related_suggestions_story') # Garder commenté

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Statut")
    submitted_on = models.DateTimeField(auto_now_add=True, verbose_name="Soumis le")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Notes de l'Administrateur")

    def __str__(self):
        user_info = self.user.username if self.user else self.name_or_email or "Anonyme"
        return f"{self.get_submission_type_display()} - {self.title[:50]} (par {user_info})"

    class Meta:
        verbose_name = "Suggestion Utilisateur"
        verbose_name_plural = "Suggestions des Utilisateurs"
        ordering = ['-submitted_on']