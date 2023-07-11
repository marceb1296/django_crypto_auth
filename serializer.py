from rest_framework import serializers
from django.contrib.auth.models import User

from .models import CryptoToken
from .app_settings import crypto_auth_setting


class UserSerializer(serializers.ModelSerializer):
    
    user = serializers.StringRelatedField(source="user.username")

    class Meta:
        model = User
        fields = ('user',)



class TokenSerializer(serializers.ModelSerializer):

    token = serializers.CharField(source='key')
    refresh_token = serializers.SerializerMethodField()
    expiry = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = CryptoToken
        fields = ('token', 'expiry', 'refresh_token', "user")


    def get_refresh_token(self, obj):
        if hasattr(obj, "get_refresh_token"):
            return obj.get_refresh_token
        return None
    
    def get_expiry(self, obj):
        if hasattr(obj, "get_expiry"):
            return obj.get_expiry
        return None
    
    
    def get_user(self, obj):
        if self.context.get("user"):
            return UserSerializer(self.context["user"]).data
        return None

