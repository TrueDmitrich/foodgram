import base64
from collections import Counter

from django.core.files.base import ContentFile
from rest_framework import serializers


def empty_list(value):
    if not value:
        raise serializers.ValidationError('Пустое значение.')
    return value


def validate_duplicates_in_list(values, value_name):
    if len(values) != len(set(values)):
        duplicate_list = [
            name for name, count in Counter(values).items() if count > 1]
        raise serializers.ValidationError(
            f'Дублирующиеся {value_name}: {duplicate_list}.')
    return values


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
