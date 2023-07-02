from django.db import models
from django.contrib.auth.models import User
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from .cryptoAuth import CryptoAuthentication
from django.utils import timezone
from django.core.exceptions import ValidationError

try:
    from .app_settings import crypto_auth_setting
except:
    raise ImproperlyConfigured("Missing crypto_auth settings")
    

# Create your models here.

class AuthTokenManager(models.Manager):
    
    def create(
            self, 
            user, 
            expiry=crypto_auth_setting.get_token_expiry
        ):

        for _token in user.auth_crypto.all():
            if _token.expiry < timezone.now():
                    _token.delete()

        if user.auth_crypto.count() >= crypto_auth_setting.max_token_per_user:
            raise ValidationError("Maximum amount of tokens allowed per user exceeded.")

        token = CryptoAuthentication()
        key_encrypted  = token.key(token.generate_token)
        key = token.combine_key_with_token(key_encrypted)
        
        expiry = timezone.now() + expiry
        instance = super(AuthTokenManager, self).create(
            user=user,
            key=key,
            expiry=expiry
        )

        return instance


class AbstractCryptoAuthToken(models.Model):

    user = models.ForeignKey(User, null=False, blank=False, related_name='auth_crypto', on_delete=models.CASCADE)
    key = models.CharField(max_length=64, blank=False, null=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField(null=True, blank=True)

    objects = AuthTokenManager()


    class Meta:
        abstract = True
        ordering = ["expiry"]

    @property
    def get_token_key(self) -> str:
        crypto = CryptoAuthentication()
        key = crypto.token_key(self.key, subset=True)
        return crypto.decript_key(key, crypto_auth_setting.get_token_shuffle)
    
    @property
    def get_expiry(self):
        return int(crypto_auth_setting.get_token_expiry.total_seconds())
    
    @property
    def get_refresh_token(self) -> str:
        crypto = CryptoAuthentication()
        key = crypto.token_key(self.key, subset=True)
        return crypto.combine_key_with_token(key[::-1])


    def __str__(self):
        return '%s : %s' % (self.user, self.key)
    

class CryptoToken(AbstractCryptoAuthToken):
    class Meta:
        swappable = crypto_auth_setting.token_model


def get_token_model():
    """
    Return the Token model that is active in this project.
    """

    try:
        return apps.get_model(crypto_auth_setting.token_model, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "CRYPTO_AUTH_TOKEN_MODEL has to be set: 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "CRYPTO_AUTH_TOKEN_MODEL refers to model '%s' that has not been installed"
            % crypto_auth_setting.token_model
        )
    
    
