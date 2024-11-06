# Заполнение базы
from recipes.models import Tag, Ingredient
import csv


tag_list = ['tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5']
tag_object_list = [Tag(name=tag, slug=tag) for tag in tag_list]


def dump():
    for tag in tag_object_list:
        _, __ = Tag.objects.get_or_create(name=tag, slug=tag)
    with open('ingredients.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            _, __ = Ingredient.objects.get_or_create(
                name=row['name'], measurement_unit=row['unit'])
