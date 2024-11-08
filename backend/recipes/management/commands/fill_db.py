# Заполнение базы
from django.core.management import BaseCommand

from recipes.models import Tag, Ingredient
import json


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('data/ingredients.json', 'r', encoding='utf-8') as file:
            Ingredient.objects.bulk_create((
                Ingredient(**ingredient_json)
                for ingredient_json in json.load(file)
            ), ignore_conflicts=True)

        with open('data/tags.json', 'r', encoding='utf-8') as file:
            Tag.objects.bulk_create((
                Tag(name=tag_name['name'],
                    slug=tag_name['name']
                    ) for tag_name in json.load(file)
            ), ignore_conflicts=True)
