from pprint import pprint

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.fields import empty

from api.models import User
from api.serializers_fields import ImageBase64Field


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = ImageBase64Field(required=False)


    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')
    def get_is_subscribed(self, obj):
        if self.context["request"].user.is_authenticated:
            return obj in self.context["request"].user.follows.all()
        return False

    def run_validation(self, data=empty):
        if self.context["request"].method == "PUT":
            self.fields.fields['avatar'].required = True
        return super().run_validation(data)



