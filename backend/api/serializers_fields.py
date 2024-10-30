import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

def base64_validator(value):
    # raise serializers.ValidationError(code='required')
    return value

class ImageBase64Field(serializers.ImageField):
    """Изображение в формате base 64."""

    validators = [base64_validator]
    default_error_messages = {
        'required': 'This field is required.',
        'invalid_image': (
            'Upload a valid image. The file you uploaded was either not an image or a corrupted image.'
        ),
    }

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            return super().to_internal_value(data)
        # raise serializers.ValidationError(self.default_error_messages['invalid_image'])
        raise serializers.ValidationError(code='invalid_image')