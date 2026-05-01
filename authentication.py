# pyright: reportGeneralTypeIssues=false
from django.core.cache import cache
import re

from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header,
)
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .app_settings import crypto_auth_setting
from .models import get_token_model, CryptoToken
from .cryptoAuth import CryptoAuthentication


class TokenAuthentication(BaseAuthentication):

    """
    Custom token based authentication with a refreshed token.
    Clients should authenticate by passing a custom key in the "Authorization"
    HTTP header, prepended with a custom string set by the user.  For example:
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = crypto_auth_setting.token_keyword
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
        # Deterministic cleanup: Every 5 minutes, clean expired tokens.
        # Uses cache to coordinate across all processes without hitting the DB every time.
        if cache.add("crypto_auth_cleanup_lock", True, 300):
            get_token_model().objects.filter(expiry__lt=timezone.now()).delete()

        # 1. Extract the "signal" from the provided token.
        # This is what db_token[::subset_length] MUST match.
        target_subset = self.crypto.token_key(key, subset=True)

        if self.is_refresh_token:
            # Refresh tokens match the reversed decrypted key.
            target_subset = target_subset[::-1]

        # 2. Build a regex to filter tokens in the database.
        # This avoids fetching and processing invalid tokens in Python.
        step = self.crypto.subset_length
        regex_parts = []
        for i, char in enumerate(target_subset):
            regex_parts.append(re.escape(char))
            if i < len(target_subset) - 1:
                regex_parts.append(f".{{{step-1}}}")

        token_regex = "^" + "".join(regex_parts)

        # 3. Query the database using the regex filter.
        # We add key__startswith for a fast B-Tree index lookup before the regex.
        # We don't filter by expiry in SQL so we can return a "Token expired" message.
        candidate_tokens = (
            get_token_model()
            .objects.filter(
                key__startswith=target_subset[0],
                key__regex=token_regex,
            )
            .select_related("user")
        )

        for get_token in candidate_tokens:
            if self._verify_token(get_token, key):

                if get_token.expiry < timezone.now():
                    # For security and cleanup, we could delete it here,
                    # but we'll stick to just raising the error as per test expectations.
                    raise AuthenticationFailed(_("Token expired."))

                if not get_token.user.is_active:
                    msg = _("User inactive or deleted.")
                    raise AuthenticationFailed(msg)

                return get_token.user, get_token

        raise AuthenticationFailed(_("Invalid token."))


    def authenticate_header(self, request):
        return self.keyword
    

    def _verify_token(self, query: CryptoToken, key: str) -> bool:
        _key_query = query.get_token_key
        _key_token = self.crypto.token_key(key, subset=True)
        _key_token_decrypted = self.crypto.decrypt_key(_key_token, crypto_auth_setting.get_token_shuffle)

        if self.is_refresh_token:
            return self.crypto.verify_key(_key_query, _key_token_decrypted[::-1])

        return self.crypto.verify_key(_key_query, _key_token_decrypted)
    
class RefreshTokenAuthentication(TokenAuthentication):
    is_refresh_token = True

