import json

from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('data/tags.json', 'r', encoding='utf-8') as file:
            Tag.objects.bulk_create((
                Tag(**tag_json)
                for tag_json in json.load(file)
            ), ignore_conflicts=True)
