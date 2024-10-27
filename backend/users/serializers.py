from rest_framework import serializers

from api.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    # avatar = serializers.SerializerMethodField() # Разобраться

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        # print(obj)
        # print(self.context["request"].user)
        return obj in self.context["request"].user.follows.all()