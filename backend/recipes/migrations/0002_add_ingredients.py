import json

from django.db import migrations

with open('recipes/migrations/ingredients.json', 'r', encoding='utf-8') as f:
    ingredients = json.load(f)


def remove_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    for ingredient in ingredients:
        Ingredient.objects.get(name=ingredient['name']).delete()


def add_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    for ingredient in ingredients:
        new_ingredient = Ingredient(**ingredient)
        new_ingredient.save()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_ingredients,
            remove_ingredients
        ),
    ]
