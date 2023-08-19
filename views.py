from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework import status
from django.db.models import Model
from rest_framework import serializers
from django.utils.module_loading import import_string

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
            serializerClass = import_string(self.serializer)
            if not isinstance(serializerClass(), serializers.Serializer):
                raise TypeError("""
                    CRYPTO_AUTH_TOKEN_SERIALIZER must be a Serializer instance, got %s
                """ % serializerClass().__class__.__name__)
            
            return serializerClass
        else:
            from .serializer import TokenSerializer
            self.serializer = TokenSerializer
        
        return self.serializer


    def get_response_data(self, obj: Model) -> dict:

        serializer = self.get_serializer

        return serializer(obj, context={
			"user": obj.user
		}).data
    

    def get_response(self, request):
        try:
            instance = get_token_model().objects.create(user=request.user)
            return Response(self.get_response_data(instance), status=status.HTTP_200_OK)
        except ValidationError as e:
            
            return Response({"detail": str(e.message)}, status=status.HTTP_403_FORBIDDEN)


    def post(self, request):
        return self.get_response(request)
    

class UpdateLoginView(LoginView):
    authentication_classes = [RefreshTokenAuthentication]

    def put(self, request):

        token = request.auth
        if token is not None:
            token.delete()
            
        instance = get_token_model().objects.create(user=request.user)

        return Response(self.get_response_data(instance), status=status.HTTP_200_OK)


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



# Only for Test Case
class MyTestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "Success"
        }, status.HTTP_200_OK)