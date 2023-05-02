from rest_framework import serializers

from .models import CryptoToken
from .app_settings import crypto_auth_setting


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    token = serializers.CharField(source='key')
    refresh_token = serializers.SerializerMethodField()
    expiry = serializers.SerializerMethodField()

    class Meta:
        model = CryptoToken
        fields = ('token', 'expiry', 'refresh_token', "username")


    def get_refresh_token(self, obj):
        if hasattr(obj, "get_refresh_token"):
            return obj.get_refresh_token
        return None
    
    def get_expiry(self, obj):
        if hasattr(obj, "get_expiry"):
            return obj.get_expiry
        return None

