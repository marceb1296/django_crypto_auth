from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Model
from rest_framework import serializers

from .models import get_token_model
from .app_settings import crypto_auth_setting
from .authentication import TokenAuthentication, RefreshTokenAuthentication

# Create your views here.


class LoginView(APIView):

    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated,)
    serializer = getattr(settings, 'CRYPTO_AUTH_TOKEN_SERIALIZER', None)

    @property
    def get_serializer(self):
        if self.serializer:

            if not isinstance(self.serializer(), serializers.Serializer):
                raise TypeError("""
                    CRYPTO_AUTH_TOKEN_SERIALIZER must be a Serializer instance, got %s
                """ % self.serializer.__class__.__name__) # type: ignore
        else:
            from .serializer import TokenSerializer
            self.serializer = TokenSerializer
        
        return self.serializer


    def get_response_data(self, obj: Model) -> dict:

        serializer = self.get_serializer

        return serializer(obj).data


    def post(self, request):

        if request.user.auth_crypto.count() >= crypto_auth_setting.max_token_per_user:
            return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN
                )

        instance = get_token_model().objects.create(user=request.user)

        return Response(self.get_response_data(instance), status=200)
    

class UpdateLoginView(LoginView):
    authentication_classes = [RefreshTokenAuthentication]

    def put(self, request):

        token = request.auth
        if token is not None:
            token.delete()
            
        instance = get_token_model().objects.create(user=request.user)

        return Response(self.get_response_data(instance), status=200)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        token = request.auth
        if token is not None:
            token.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    

class LogoutAllView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        request.user.auth_crypto.all().delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


