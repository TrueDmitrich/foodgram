import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


def empty_list(value):
    if not value:
        raise serializers.ValidationError('Empty list.')
    return value


def search_duplicates_in_list(values):
    duplicate_set = set()
    while True:
        value = values.pop()
        if value in values:
            duplicate_set.add(value)
        if not values:
            break
    return duplicate_set


def unique_ingredients(ingredients):
    ingredients_list = [ing['ingredient'] for ing in ingredients]
    if len(ingredients) != len(set(ingredients_list)):
        duplicate_set = search_duplicates_in_list(ingredients_list)
        raise serializers.ValidationError(
            f'Дублирующиеся ингредиенты: {duplicate_set}.')
    return ingredients


def unique_tags(tags):
    if len(tags) != len(set(tags)):
        duplicate_set = search_duplicates_in_list(tags)
        raise serializers.ValidationError(
            f'Дублирующиеся теги: {duplicate_set}.')
    return tags


class Base64ImageField(serializers.ImageField):
    """Изображение в формате base 64."""

    default_error_messages = {
        'required': 'This field is required.',
        'invalid_image': (
            'Upload a valid image. The file you uploaded was '
            + 'either not an image or a corrupted image.'
        ),
    }

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            return super().to_internal_value(data)
        raise serializers.ValidationError(code='invalid_image')
