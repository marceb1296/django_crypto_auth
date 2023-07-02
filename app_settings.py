from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from . import helper


class CryptoAuthDefaultSettings:

    default_lenght = 32
    length_token = 64

    def __setattr__(self) -> None:
        raise Exception('''
            %s values must NEVER be changed at runtime,
                Cause they are part of database
                        ''' % self.__class__.__name__)

    
class CryptoAuthSettings:

    token_model = getattr(settings, 'CRYPTO_AUTH_TOKEN_MODEL', 'django_crypto_auth.CryptoToken')
    
    @property 
    def token_keywoard(self):
        token_keywoard = getattr(settings, 'CRYPTO_AUTH_TOKEN_KEYWOARD', 'TSESSION')
        
        if not isinstance(token_keywoard, str):
            raise TypeError("""
                CRYPTO_AUTH_MAX_TOKEN_LIMIT value must be str, got %s
            """ % token_keywoard.__class__.__name__)

        return token_keywoard


    @property
    def max_token_per_user(self):
        max_token_per_user = getattr(settings, 'CRYPTO_AUTH_MAX_TOKEN_LIMIT', 2)
        if not isinstance(max_token_per_user, int):
            raise TypeError("""
                CRYPTO_AUTH_MAX_TOKEN_LIMIT value must be Integer
            """)
        
        return max_token_per_user


    @property
    def subset_length(self):

        subset_length = getattr(settings, "CRYPTO_AUTH_SUBSET_LENGTH", 4)
        
        if not isinstance(subset_length, int):
            raise TypeError("""
                CRYPTO_AUTH_SUBSET_LENGTH value must be an Integer
            """)
        
        if subset_length > 15 or subset_length < 2:
            raise ImproperlyConfigured("""
                CRYPTO_AUTH_SUBSET_LENGTH value must be among 2 and 15
            """)
        
        return subset_length


    @property
    def get_token_expiry(self):

        get_token_expiry = getattr(settings, "CRYPTO_AUTH_TOKEN_EXPIRY", ("minutes", 3))

        if not isinstance(get_token_expiry, list) and not isinstance(get_token_expiry, tuple):
            raise ImproperlyConfigured("""
                CRYPTO_AUTH_TOKEN_EXPIRY must be a list or tuple, got %s
            """ % get_token_expiry.__class__.__name__)
        
        if not isinstance(get_token_expiry[0], str):
            raise ImproperlyConfigured("""
                CRYPTO_AUTH_TOKEN_EXPIRY first element must be a str, got %s
            """ % get_token_expiry[0].__class__.__name__)
        
        if not isinstance(get_token_expiry[1], int):
            raise ImproperlyConfigured("""
                CRYPTO_AUTH_TOKEN_EXPIRY second element must be a int got %s
            """ % get_token_expiry[0].__class__.__name__)
        
        token_expiry = helper.expired_time.get(get_token_expiry[0])
        
        if not token_expiry:
            raise ImproperlyConfigured("""
                CRYPTO_AUTH_TOKEN_EXPIRY first element must be equal to one of the following keys;
                    %s

            """ % "\n".join(helper.expired_time.keys()))

        return token_expiry(get_token_expiry[1])


    @property
    def get_token_shuffle(self):
        
        shuffle = getattr(settings, "CRYPTO_AUTH_TOKEN_SHUFFLE", None)
        shuffle_from_helper = getattr(helper, "CRYPTO_AUTH_TOKEN_SHUFFLE", None)

        if shuffle_from_helper:
            return shuffle_from_helper

        if not shuffle:
            raise ImproperlyConfigured("""
                Can´t find CRYPTO_AUTH_TOKEN_SHUFFLE into settings.py
                    perhaps, 
                        did you forget set it?
            """)

        if not isinstance(shuffle, (tuple, list)):
            raise ImproperlyConfigured("""
                CRYPTO_AUTH_TOKEN_SHUFFLE must be both; tuple or list, got %s

            """ % shuffle.__class__.__name__ )
        
        return shuffle
        

    

crypto_auth_default_setting = CryptoAuthDefaultSettings()
crypto_auth_setting = CryptoAuthSettings()