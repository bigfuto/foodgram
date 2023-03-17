from django.db import migrations

TAGS = [
    {'name': 'Завтрак', 'color': '#339900', 'slug': 'breakfast'},
    {'name': 'Обед', 'color': '#FFCC33', 'slug': 'lunch'},
    {'name': 'Ужин', 'color': '#CC0000', 'slug': 'dinner'},
]


def remove_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    for tag in TAGS:
        Tag.objects.get(slug=tag['slug']).delete()


def add_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    for tag in TAGS:
        new_tag = Tag(**tag)
        new_tag.save()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_add_ingredients'),
    ]

    operations = [
        migrations.RunPython(
            add_tags,
            remove_tags
        ),
    ]
