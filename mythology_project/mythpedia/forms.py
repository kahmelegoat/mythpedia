# mythpedia/forms.py
from django import forms
from .models import Suggestion, Mythology, Character

class SuggestionForm(forms.ModelForm):
    # Définir les champs ici permet de personnaliser le widget et les attributs
    # même s'ils sont aussi listés dans Meta.fields.
    # Ce qui est défini ici prendra le pas sur la génération par défaut de ModelForm pour ces champs.

    submission_type = forms.ChoiceField(
        choices=Suggestion.SUBMISSION_TYPES, # Utiliser les choices du modèle
        label="Quel type de suggestion souhaitez-vous faire ?",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md shadow-sm'
        })
    )
    title = forms.CharField(
        label="Titre ou Sujet Principal",
        widget=forms.TextInput(attrs={
            'placeholder': 'Sujet de votre suggestion',
            'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
        })
    )
    description = forms.CharField(
        label="Votre Suggestion Détaillée",
        widget=forms.Textarea(attrs={
            'rows': 5, 
            'placeholder': 'Décrivez votre suggestion en détail...',
            'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
        })
    )
    name_or_email = forms.CharField(
        max_length=150, 
        required=False, 
        label="Votre Nom ou Email (optionnel si connecté)",
        widget=forms.TextInput(attrs={
            'placeholder': 'Si vous souhaitez être contacté (optionnel)', # Placeholder mis à jour
            'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
        })
    )
    related_mythology = forms.ModelChoiceField(
        queryset=Mythology.objects.all().order_by('title'), 
        required=False,
        label="Mythologie Concernée (pour une correction)",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md shadow-sm form-select' # Ajout de form-select si vous avez des styles spécifiques
        })
    )
    related_character = forms.ModelChoiceField(
        queryset=Character.objects.all().order_by('name'), 
        required=False,
        label="Personnage Concerné (pour une correction)",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md shadow-sm form-select' # Ajout de form-select
        })
    )

    class Meta:
        model = Suggestion
        # Lister tous les champs que le formulaire doit gérer
        fields = ['submission_type', 'title', 'description', 'name_or_email', 'related_mythology', 'related_character']
        # Les widgets définis ci-dessus pour les champs spécifiques surchargeront ceux générés par défaut.
        # Vous n'avez plus besoin de la section 'widgets' dans Meta si tous les champs sont définis explicitement au-dessus.
        # labels = { ... } # Les labels sont déjà définis sur les champs ci-dessus.

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Logique pour le champ name_or_email basé sur l'authentification de l'utilisateur
        if self.user and self.user.is_authenticated:
            self.fields['name_or_email'].required = False
            self.fields['name_or_email'].widget = forms.HiddenInput() # Masquer si connecté
            # Vous pourriez vouloir pré-remplir le champ user dans la vue au lieu de le masquer complètement ici,
            # ou simplement ne pas rendre ce champ du tout dans le template si user est authentifié.
            # Mais pour la logique actuelle, le masquer est simple.
        else:
            self.fields['name_or_email'].required = True # Rendre requis pour les anonymes
            # S'assurer que le widget n'est pas caché si requis
            if isinstance(self.fields['name_or_email'].widget, forms.HiddenInput):
                 self.fields['name_or_email'].widget = forms.TextInput(attrs={
                    'placeholder': 'Votre nom ou email (requis)',
                    'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
                })

        # Logique initiale pour masquer les champs "related_" (le JS s'en chargera dynamiquement)
        # Ces champs ne sont utiles que si submission_type est 'CORRECTION'
        # if self.initial.get('submission_type') != 'CORRECTION' and (not self.data or self.data.get('submission_type') != 'CORRECTION'):
        #     self.fields['related_mythology'].widget = forms.HiddenInput()
        #     self.fields['related_character'].widget = forms.HiddenInput()
        # Le script JS dans le template est une meilleure approche pour la dynamicité.