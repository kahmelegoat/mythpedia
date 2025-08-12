# mythpedia/management/commands/seed_mythologies.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify # Inclus dans les modèles, mais bon de l'avoir ici si besoin
from mythpedia.models import Mythology, Character

# VOS DONNÉES (COPIÉES DEPUIS VOTRE HTML/JS)
# J'ai légèrement adapté les noms de clés pour correspondre aux modèles Django si besoin
# (ex: 'icon' devient 'icon_class', 'colorFrom' devient 'color_from')
MYTHOLOGIES_DATA_FROM_JS = {
    'chinese': {
        'title': "Chinoise",
        'icon_class': "fa-dragon", # Adapté de 'icon'
        'color_from': "from-red-500", # Adapté de 'colorFrom'
        'color_to': "to-yellow-400",   # Adapté de 'colorTo'
        'description': "La mythologie chinoise regroupe un ensemble de récits et de légendes issus de la tradition orale et écrite de la Chine ancienne. Elle comprend des divinités, des héros culturels, des créatures fantastiques et des récits cosmogoniques. Le taoïsme, le confucianisme et le bouddhisme ont fortement influencé cette mythologie. Parmi les concepts clés, on trouve le Yin et Yang, les Trois Purs et les divinités comme l'Empereur de Jade.",
        'card_summary': "Divinités, héros et créatures de la Chine ancienne.", # Ajouté pour l'exemple
        'characters': [
            { 'name': "Pangu", 'role': "Créateur de l'univers", 'description': "Premier être vivant qui a séparé le ciel et la terre.", 'image_url': "https://i.imgur.com/JQ6Xg0W.png" },
            { 'name': "Nuwa", 'role': "Déesse créatrice", 'description': "A créé les humains à partir d'argile et réparé le ciel.", 'image_url': "https://i.imgur.com/vW5T3hG.png" },
            { 'name': "Fuxi", 'role': "Empereur mythique", 'description': "A enseigné aux humains la chasse, la pêche et l'écriture.", 'image_url': "https://i.imgur.com/9zQY2Jj.png" },
            { 'name': "L'Empereur de Jade", 'role': "Souverain du ciel", 'description': "Dirige le panthéon des dieux dans le ciel taoïste.", 'image_url': "https://i.imgur.com/8K3Lm9X.png" },
            { 'name': "Guanyin", 'role': "Déesse de la miséricorde", 'description': "Bodhisattva de la compassion dans le bouddhisme.", 'image_url': "https://i.imgur.com/4j7VQ2t.png" }
        ]
    },
    'nordic': {
        'title': "Mythologie Nordique",
        'icon_class': "fa-helmet-battle",
        'color_from': "from-gray-700",
        'color_to': "to-blue-900",
        'description': "La mythologie nordique est l'ensemble des mythes provenant d'Europe du Nord (Scandinavie, Islande, etc.) à l'époque viking. Elle met en scène des dieux comme Odin, Thor et Loki, et décrit un univers composé de neuf mondes reliés par l'arbre Yggdrasil. Les récits principaux incluent la création du monde, les aventures des dieux et le Ragnarök, la fin du monde prophétique.",
        'card_summary': "Dieux guerriers et neuf mondes vikings.",
        'characters': [
            { 'name': "Odin", 'role': "Père des dieux", 'description': "Dieu de la sagesse, de la guerre et de la poésie.", 'image_url': "https://i.imgur.com/3Qm7z9G.png" },
            { 'name': "Thor", 'role': "Dieu du tonnerre", 'description': "Protecteur des humains, armé de son marteau Mjöllnir.", 'image_url': "https://i.imgur.com/Vg5LtY9.png" },
            { 'name': "Loki", 'role': "Dieu de la malice", 'description': "Esprit de la tromperie, à la fois allié et ennemi des dieux.", 'image_url': "https://i.imgur.com/9XjKQ2H.png" },
            { 'name': "Freyja", 'role': "Déesse de l'amour", 'description': "Déesse de la fertilité, de l'amour et de la beauté.", 'image_url': "https://i.imgur.com/7J8k9ZL.png" },
            { 'name': "Tyr", 'role': "Dieu de la guerre", 'description': "Dieu du droit et de la justice héroïque.", 'image_url': "https://i.imgur.com/5tK3j9M.png" }
        ]
    },
    'greek': {
        'title': "Mythologie Grecque",
        'icon_class': "fa-landmark",
        'color_from': "from-blue-400",
        'color_to': "to-purple-600",
        'description': "La mythologie grecque est l'ensemble des mythes et légendes provenant de la Grèce antique. Elle se compose principalement de récits sur les dieux du panthéon grec, les héros et les créatures mythologiques. Les dieux principaux, dirigés par Zeus, vivent sur le mont Olympe. Les mythes grecs expliquent l'origine du monde, les phénomènes naturels et enseignent des leçons morales à travers des histoires comme celles d'Hercule, d'Ulysse ou de Persée.",
        'card_summary': "Dieux de l'Olympe et héros légendaires.",
        'characters': [
            { 'name': "Zeus", 'role': "Roi des dieux", 'description': "Dieu du ciel et du tonnerre, souverain de l'Olympe.", 'image_url': "https://i.imgur.com/1Q9Z9JX.png" },
            { 'name': "Athéna", 'role': "Déesse de la sagesse", 'description': "Déesse de la stratégie guerrière et de la raison.", 'image_url': "https://i.imgur.com/3Kj9L2X.png" },
            { 'name': "Poséidon", 'role': "Dieu de la mer", 'description': "Frère de Zeus, maître des océans et des tremblements de terre.", 'image_url': "https://i.imgur.com/7J8k9ZL.png" }, # Image potentiellement dupliquée, vérifiez vos sources
            { 'name': "Aphrodite", 'role': "Déesse de l'amour", 'description': "Née de l'écume de mer, personnification de la beauté.", 'image_url': "https://i.imgur.com/4j7VQ2t.png" }, # Image potentiellement dupliquée
            { 'name': "Héraclès", 'role': "Héros mythique", 'description': "Plus grand héros grec, connu pour ses douze travaux.", 'image_url': "https://i.imgur.com/Vg5LtY9.png" } # Image potentiellement dupliquée
        ]
    },
    'egyptian': {
        'title': "Mythologie Égyptienne",
        'icon_class': "fa-ankh",
        'color_from': "from-yellow-600",
        'color_to': "to-orange-600",
        'description': "La mythologie égyptienne est l'ensemble des mythes religieux de l'Égypte antique. Elle est centrée sur les dieux comme Râ, Osiris, Isis et Horus, et sur les concepts de mort, de renaissance et de jugement des âmes. Les Égyptiens croyaient en une vie après la mort, d'où l'importance des rituels funéraires et de la momification. Les mythes expliquent la création du monde, le cycle du soleil et le combat entre l'ordre (Maât) et le chaos (Isfet).",
        'card_summary': "Rituels funéraires et dieux à tête d'animal.",
        'characters': [
            { 'name': "Râ", 'role': "Dieu du soleil", 'description': "Créateur et souverain des dieux, voyage dans la barque solaire.", 'image_url': "https://i.imgur.com/8K3Lm9X.png" },
            { 'name': "Osiris", 'role': "Dieu des morts", 'description': "Roi du monde souterrain après avoir été assassiné par Seth.", 'image_url': "https://i.imgur.com/9zQY2Jj.png" },
            { 'name': "Isis", 'role': "Déesse magicienne", 'description': "Épouse d'Osiris, symbole de la maternité et de la magie.", 'image_url': "https://i.imgur.com/4j7VQ2t.png" },
            { 'name': "Horus", 'role': "Dieu faucon", 'description': "Fils d'Isis et Osiris, dieu du ciel et de la royauté.", 'image_url': "https://i.imgur.com/JQ6Xg0W.png" },
            { 'name': "Anubis", 'role': "Dieu des embaumeurs", 'description': "Guide des âmes et dieu de la momification.", 'image_url': "https://i.imgur.com/3Qm7z9G.png" }
        ]
    },
    'japanese': {
        'title': "Mythologie Japonaise",
        'icon_class': "fa-torii-gate",
        'color_from': "from-red-600",
        'color_to': "to-pink-500",
        'description': "La mythologie japonaise est un système complexe de croyances qui mêle le shintoïsme et le bouddhisme. Elle inclut les kami (esprits ou dieux), les créatures légendaires comme les yokai, et des récits cosmogoniques comme la création du Japon par Izanagi et Izanami. Les mythes sont principalement consignés dans le Kojiki et le Nihon Shoki. Le shintoïsme, religion indigène du Japon, vénère les forces de la nature et les ancêtres à travers ces mythes.",
        'card_summary': "Kami, yokai et légendes du pays du soleil levant.",
        'characters': [
            { 'name': "Amaterasu", 'role': "Déesse du soleil", 'description': "Kami du soleil, ancêtre mythique de la famille impériale.", 'image_url': "https://i.imgur.com/7J8k9ZL.png" },
            { 'name': "Susanoo", 'role': "Dieu des tempêtes", 'description': "Frère d'Amaterasu, kami des mers et des tempêtes.", 'image_url': "https://i.imgur.com/Vg5LtY9.png" },
            { 'name': "Izanagi & Izanami", 'role': "Créateurs du Japon", 'description': "Couple divin ayant créé les îles japonaises.", 'image_url': "https://i.imgur.com/9zQY2Jj.png" },
            { 'name': "Tsukuyomi", 'role': "Dieu de la lune", 'description': "Kami de la lune, frère d'Amaterasu.", 'image_url': "https://i.imgur.com/8K3Lm9X.png" },
            { 'name': "Inari", 'role': "Dieu/déesse du riz", 'description': "Kami de la fertilité, du riz et des renards.", 'image_url': "https://i.imgur.com/JQ6Xg0W.png" }
        ]
    },
    # ... AJOUTEZ TOUTES LES AUTRES MYTHOLOGIES DE VOTRE FICHIER HTML ICI ...
    # En respectant la même structure et en adaptant les clés si besoin
    # (icon_class, color_from, color_to, card_summary, et image_url pour les personnages)
    'roman': {
        'title': "Mythologie Romaine", 'icon_class': "fa-archway", 'color_from': "from-purple-700", 'color_to': "to-red-700",
        'description': "La mythologie romaine est l'ensemble des légendes et des mythes de la Rome antique...",
        'card_summary': "Les dieux et héros de l'Empire Romain, inspirés des Grecs.",
        'characters': [
            {'name': "Jupiter", 'role': "Roi des dieux", 'description': "Équivalent romain de Zeus...", 'image_url': "https://i.imgur.com/1Q9Z9JX.png"},
            # ... autres personnages romains
        ]
    },
    'celtic': {
        'title': "Mythologie Celtique", 'icon_class': "fa-tree", 'color_from': "from-green-700", 'color_to': "to-blue-700",
        'description': "La mythologie celtique regroupe les croyances des peuples celtes d'Europe...",
        'card_summary': "Druides, héros et créatures magiques des terres celtes.",
        'characters': [
            {'name': "Dagda", 'role': "Dieu bon", 'description': "Père des dieux...", 'image_url': "https://i.imgur.com/9zQY2Jj.png"},
            # ... autres personnages celtes
        ]
    },
    'aztec': {
        'title': "Mythologie Aztèque", 'icon_class': "fa-sun", 'color_from': "from-orange-700", 'color_to': "to-yellow-600",
        'description': "La mythologie aztèque est l'ensemble des croyances du peuple aztèque...",
        'card_summary': "Cosmogonie complexe et dieux du Mexique central précolombien.",
        'characters': [
            {'name': "Quetzalcoatl", 'role': "Serpent à plumes", 'description': "Dieu de la sagesse...", 'image_url': "https://i.imgur.com/JQ6Xg0W.png"},
            # ... autres personnages aztèques
        ]
    },
    'hindu': {
        'title': "Mythologie Hindoue", 'icon_class': "fa-om", 'color_from': "from-indigo-700", 'color_to': "to-purple-500",
        'description': "La mythologie hindoue est riche et complexe, avec des textes sacrés comme les Vedas...",
        'card_summary': "Trimurti, avatars et cycles cosmiques de l'Inde.",
        'characters': [
            {'name': "Brahma", 'role': "Dieu créateur", 'description': "Premier membre de la Trimurti...", 'image_url': "https://i.imgur.com/9zQY2Jj.png"},
            # ... autres personnages hindous
        ]
    },
    'inca': {
        'title': "Mythologie Inca", 'icon_class': "fa-mountain", 'color_from': "from-amber-700", 'color_to': "to-yellow-500",
        'description': "La mythologie inca est l'ensemble des mythes et légendes de l'Empire inca...",
        'card_summary': "Culte du Soleil et divinités des Andes.",
        'characters': [
            {'name': "Inti", 'role': "Dieu du soleil", 'description': "Divinité suprême...", 'image_url': "https://i.imgur.com/8K3Lm9X.png"},
            # ... autres personnages incas
        ]
    },
    'mesopotamian': {
        'title': "Mythologie Mésopotamienne", 'icon_class': "fa-scroll", 'color_from': "from-stone-700", 'color_to': "to-amber-600",
        'description': "La mythologie mésopotamienne est l'une des plus anciennes connues...",
        'card_summary': "Épopées anciennes et dieux de Sumer et Babylone.",
        'characters': [
            {'name': "Gilgamesh", 'role': "Roi légendaire", 'description': "Héros de la première épopée...", 'image_url': "https://i.imgur.com/Vg5LtY9.png"},
            # ... autres personnages mésopotamiens
        ]
    },
    'persian': {
        'title': "Mythologie Perse", 'icon_class': "fa-fire", 'color_from': "from-rose-700", 'color_to': "to-orange-500",
        'description': "La mythologie perse provient principalement de l'Avesta...",
        'card_summary': "Dualisme zoroastrien et récits de l'Iran ancien.",
        'characters': [
            {'name': "Ahura Mazda", 'role': "Dieu suprême", 'description': "Créateur du monde...", 'image_url': "https://i.imgur.com/8K3Lm9X.png"},
            # ... autres personnages perses
        ]
    },
    'polynesian': {
        'title': "Mythologie Polynésienne", 'icon_class': "fa-water", 'color_from': "from-cyan-700", 'color_to': "to-blue-500",
        'description': "La mythologie polynésienne varie selon les îles mais partage des thèmes communs...",
        'card_summary': "Héros navigateurs et esprits des îles du Pacifique.",
        'characters': [
            {'name': "Māui", 'role': "Demi-dieu", 'description': "Héros culturel connu...", 'image_url': "https://i.imgur.com/Vg5LtY9.png"},
            # ... autres personnages polynésiens
        ]
    },
    'slavic': {
        'title': "Mythologie Slave", 'icon_class': "fa-leaf", 'color_from': "from-emerald-700", 'color_to': "to-green-500",
        'description': "La mythologie slave provient des croyances des peuples slaves avant leur christianisation...",
        'card_summary': "Dieux du tonnerre, esprits de la nature et folklore ancien.",
        'characters': [
            {'name': "Perun", 'role': "Dieu du tonnerre", 'description': "Dieu suprême...", 'image_url': "https://i.imgur.com/Vg5LtY9.png"},
            # ... autres personnages slaves
        ]
    },
    'aboriginal': {
        'title': "Mythologie Aborigène", 'icon_class': "fa-dot-circle", 'color_from': "from-orange-600", 'color_to': "to-red-500",
        'description': "La mythologie aborigène australienne est basée sur le concept du Temps du Rêve...",
        'card_summary': "Temps du Rêve et êtres ancestraux d'Australie.",
        'characters': [
            {'name': "Serpent Arc-en-Ciel", 'role': "Être créateur", 'description': "Puissant esprit associé...", 'image_url': "https://i.imgur.com/JQ6Xg0W.png"},
            # ... autres personnages aborigènes
        ]
    }
}


class Command(BaseCommand):
    help = 'Seeds the database with initial mythology data from your JS object structure'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Vider les tables avant de peupler pour éviter les doublons (soyez prudent avec ceci)
        Character.objects.all().delete()
        Mythology.objects.all().delete()
        self.stdout.write(self.style.WARNING('Old data deleted (Mythology, Character).'))

        for slug_key, data in MYTHOLOGIES_DATA_FROM_JS.items():
            # Création de l'objet Mythology
            # Le slug est généré automatiquement par la méthode save() du modèle si slug_key n'est pas utilisé directement
            # ou si on veut une génération basée sur le titre. Ici, on utilise la clé comme slug.
            mythology_instance, created_myth = Mythology.objects.get_or_create(
                slug=slug_key, # Utiliser la clé JS comme slug
                defaults={
                    'title': data['title'],
                    'icon_class': data.get('icon_class', data.get('icon', 'fa-question-circle')), # Gère ancien nom 'icon'
                    'color_from': data.get('color_from', data.get('colorFrom', 'from-gray-500')), # Gère ancien nom 'colorFrom'
                    'color_to': data.get('color_to', data.get('colorTo', 'to-gray-700')),       # Gère ancien nom 'colorTo'
                    'description': data['description'],
                    'card_summary': data.get('card_summary', data['description'][:150] + "...")
                }
            )
            if created_myth:
                self.stdout.write(self.style.SUCCESS(f'Created Mythology: {mythology_instance.title}'))
            else:
                # Mettre à jour si elle existait déjà (optionnel, dépend de votre logique de re-seeding)
                mythology_instance.title = data['title']
                mythology_instance.icon_class = data.get('icon_class', data.get('icon', 'fa-question-circle'))
                mythology_instance.color_from = data.get('color_from', data.get('colorFrom', 'from-gray-500'))
                mythology_instance.color_to = data.get('color_to', data.get('colorTo', 'to-gray-700'))
                mythology_instance.description = data['description']
                mythology_instance.card_summary = data.get('card_summary', data['description'][:150] + "...")
                mythology_instance.save()
                self.stdout.write(self.style.WARNING(f'Updated Mythology: {mythology_instance.title}'))


            for char_data in data.get('characters', []):
                # Le slug du personnage sera généré automatiquement par la méthode save() du modèle Character
                # si le champ slug est laissé vide lors de la création.
                # Ici on utilise get_or_create pour éviter les doublons si le script est lancé plusieurs fois
                # sur la base du nom et de la mythologie.
                character_instance, created_char = Character.objects.get_or_create(
                    mythology=mythology_instance,
                    name=char_data['name'],
                    defaults={
                        'role': char_data.get('role', ''),
                        'description': char_data.get('description', ''),
                        'image_url': char_data.get('image_url', char_data.get('image', '')) # Gère ancien nom 'image'
                    }
                )
                if created_char:
                     self.stdout.write(self.style.SUCCESS(f'  - Created Character: {character_instance.name} for {mythology_instance.title}'))
                else:
                    # Mettre à jour si existant
                    character_instance.role = char_data.get('role', '')
                    character_instance.description = char_data.get('description', '')
                    character_instance.image_url = char_data.get('image_url', char_data.get('image', ''))
                    character_instance.save() # Pour s'assurer que le slug est généré si manquant, et pour sauvegarder les mises à jour
                    self.stdout.write(self.style.WARNING(f'  - Updated Character: {character_instance.name} for {mythology_instance.title}'))


        self.stdout.write(self.style.SUCCESS('Data seeding complete!'))