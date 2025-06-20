# Generated by Django 5.2.1 on 2025-05-27 15:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mythpedia', '0002_favoritemythology'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteCharacter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by_users', to='mythpedia.character')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_characters', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Personnage Favori',
                'verbose_name_plural': 'Personnages Favoris',
                'ordering': ['-added_on'],
                'unique_together': {('user', 'character')},
            },
        ),
    ]
