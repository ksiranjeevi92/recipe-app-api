# Generated by Django 3.2.25 on 2025-01-25 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_recipemodel'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipeModel',
            new_name='Recipe',
        ),
    ]
