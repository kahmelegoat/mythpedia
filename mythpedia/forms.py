# mythpedia/forms.py
from django import forms
from .models import Suggestion, Mythology, Character

class SuggestionForm(forms.ModelForm):
    # Définition des champs pour la personnalisation
    submission_type = forms.ChoiceField(
        choices=Suggestion.SUBMISSION_TYPES,
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
    # name_or_email est initialement requis pour les anonymes, on le gère dans __init__
    name_or_email = forms.CharField(
        max_length=150, 
        required=True, # Requis par défaut, sera changé dans __init__ si user est connecté
        label="Votre Nom ou Email", 
        help_text="Requis si vous n'êtes pas connecté.",
        widget=forms.TextInput(attrs={
            'placeholder': 'Votre nom ou email',
            'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
        })
    )
    related_mythology = forms.ModelChoiceField(
        queryset=Mythology.objects.all().order_by('title'), 
        required=False,
        label="Mythologie Concernée (pour une correction)",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md shadow-sm'
        })
    )
    related_character = forms.ModelChoiceField(
        queryset=Character.objects.all().order_by('name'), 
        required=False,
        label="Personnage Concerné (pour une correction)",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md shadow-sm'
        })
    )

    class Meta:
        model = Suggestion
        fields = ['submission_type', 'title', 'description', 'name_or_email', 'related_mythology', 'related_character']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) # Récupérer l'utilisateur passé depuis la vue
        super().__init__(*args, **kwargs)
        
        if user and user.is_authenticated:
            # Si l'utilisateur est connecté, on supprime le champ name_or_email du formulaire
            # Il ne sera pas rendu dans le template et sa valeur ne sera pas attendue lors de la soumission.
            # Le modèle Suggestion a user = ForeignKey(User, ..., null=True, blank=True) 
            # et name_or_email = CharField(blank=True), donc c'est OK.
            if 'name_or_email' in self.fields:
                del self.fields['name_or_email']
        else:
            # Si l'utilisateur N'EST PAS connecté, s'assurer que le champ est requis et visible
            self.fields['name_or_email'].required = True
            self.fields['name_or_email'].label = "Votre Nom ou Email (requis)"
            self.fields['name_or_email'].help_text = "Veuillez fournir votre nom ou email pour que nous puissions vous recontacter si besoin."
            # Assurer que le widget est TextInput si jamais il avait été changé
            if not isinstance(self.fields['name_or_email'].widget, forms.TextInput):
                self.fields['name_or_email'].widget = forms.TextInput(attrs=self.fields['name_or_email'].widget.attrs)