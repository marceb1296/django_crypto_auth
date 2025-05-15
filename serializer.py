from email.utils import format_datetime

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import CryptoToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="key")
    refresh_token = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    expiry_date = serializers.SerializerMethodField()

    class Meta:
        model = CryptoToken
        fields = ("token", "refresh_token", "user", "expiry_date")

    def get_refresh_token(self, obj):
        if hasattr(obj, "get_refresh_token"):
            return obj.get_refresh_token
        return None

    def get_user(self, obj):
        if self.context.get("user"):
            return UserSerializer(self.context["user"]).data
        return None

    def get_expiry_date(self, obj):
        if obj.expiry:
            # Make sure it's timezone-aware (UTC)
            return format_datetime(obj.expiry, usegmt=True)
        return None
