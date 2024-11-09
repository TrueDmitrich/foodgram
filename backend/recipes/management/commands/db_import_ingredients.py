# Заполнение базы
import json

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('data/ingredients.json', 'r', encoding='utf-8') as file:
            Ingredient.objects.bulk_create((
                Ingredient(**ingredient_json)
                for ingredient_json in json.load(file)
            ), ignore_conflicts=True)
