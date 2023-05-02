# pyright: reportGeneralTypeIssues=false
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header,
)
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .app_settings import crypto_auth_setting
from .models import get_token_model, CryptoToken
from .cryptoAuth import CryptoAuthentication
from django.db.models.query import QuerySet


class TokenAuthentication(BaseAuthentication):

    """
    Custom token based authentication with a refreshed token.
    Clients should authenticate by passing a custom key in the "Authorization"
    HTTP header, prepended with a custom string set by the user.  For example:
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = crypto_auth_setting.token_keywoard
    crypto = CryptoAuthentication()
    is_refresh_token = False

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth:
            return None
        
        if auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token)
    

    def authenticate_credentials(self, key):
        for get_token in get_token_model().objects.all(): 
            if self._verify_token(get_token, key):

                if not get_token.user.is_active:
                    msg = _('User inactive or deleted.')
                    raise AuthenticationFailed(msg)

                if get_token.expiry < timezone.now():
                    get_token.delete()
                    msg = _("Token expired.")
                    raise AuthenticationFailed(msg)
                
                return get_token.user, get_token


            if get_token.expiry < timezone.now():
                get_token.delete()
            
        raise AuthenticationFailed(_('Invalid token.'))


    def authenticate_header(self, request):
        return self.keyword
    

    def _verify_token(self, query: CryptoToken, key: str) -> bool:
        _key_query = query.get_token_key
        _key_token = self.crypto.token_key(key, subset=True)
        _key_token_decripted = self.crypto.decript_key(_key_token, crypto_auth_setting.get_token_shuffle)

        if self.is_refresh_token:
            return self.crypto.verify_key(_key_query, _key_token_decripted[::-1])

        return self.crypto.verify_key(_key_query, _key_token_decripted)
    
class RefreshTokenAuthentication(TokenAuthentication):
    is_refresh_token = True

