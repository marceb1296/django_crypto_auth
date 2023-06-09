# pyright: reportGeneralTypeIssues=false
import base64
from django.http import Http404
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone


from .models import CryptoToken, get_token_model
from .cryptoAuth import CryptoAuthentication
from .app_settings import crypto_auth_setting

from datetime import timedelta

# Create your tests here.

def get_auth_header(username, password):
    return 'Basic %s' % base64.b64encode(
        ('%s:%s' % (username, password)).encode('ascii')).decode()

@override_settings(CRYPTO_AUTH_TOKEN_SHUFFLE=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"])
class TestCryptoAuthetication(TestCase):


    def setUp(self) -> None:
        self.username = 'testuser'
        self.password = 'testpass'

        self.user = get_user_model().objects.create_user( # type: ignore
            username=self.username,
            email='testuser@example.com',
            password=self.password
        )
        self.token = get_token_model().objects.create(
            user=self.user
        )
        self.refresh_token = self.token.get_refresh_token # type: ignore
        self.client = APIClient() 

    @override_settings(CRYPTO_AUTH_TOKEN_SHUFFLE=None)
    def test_raise_error_when_token_shuffle_is_not_set(self):
        with self.assertRaises(ImproperlyConfigured):
            url = reverse("cryptoAuth_login")
            self.client.credentials(HTTP_AUTHORIZATION=get_auth_header(self.username, self.password)) 
            self.client.post(url)

    
    def test_create_token_and_refresh_token(self):
        create_user = User.objects.create(username="UserTest")
        key = CryptoToken.objects.create(create_user)

        _key = key.get_token_key

        crypto = CryptoAuthentication()

        refresh_token = key.get_refresh_token
        get_refresh_token_key = crypto.token_key(refresh_token, subset=True)
        decrypt_key = crypto.decript_key(get_refresh_token_key, crypto_auth_setting.get_token_shuffle)

        self.assertEqual(_key, decrypt_key[::-1])


    def test_create_token(self):
        url = reverse("cryptoAuth_login")
        
        self.client.credentials(HTTP_AUTHORIZATION=get_auth_header(self.username, self.password)) 
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_call_access_view_with_refresh_token(self):
        url = reverse("my_test_view")
        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.refresh_token
        ))

        response = self.client.get(url)
        to_json = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Invalid token.")


    def test_call_update_view_with_token(self):
        url = reverse("cryptoAuth_login_update")
        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.token.key
        ))

        response = self.client.get(url)
        to_json = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Invalid token.")


    @override_settings(CRYPTO_AUTH_MAX_TOKEN_LIMIT=1)
    def test_token_exceed_limit(self):

        url = reverse("cryptoAuth_login")
        self.client.credentials(HTTP_AUTHORIZATION=get_auth_header(self.username, self.password))

        response = self.client.post(url)

        to_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(to_json.get("error"), "Maximum amount of tokens allowed per user exceeded.")


    def test_token_authentication(self):
        url = reverse("my_test_view")
        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.token.key
        ))

        response = self.client.get(url)
        to_json = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(to_json.get("status"), "Success")
    
    
    def test_token_authentication_with_space(self):
        url = reverse("my_test_view")
        self.client.credentials(HTTP_AUTHORIZATION="%s 767 878" % (
            crypto_auth_setting.token_keywoard,
        ))

        response = self.client.get(url)
        to_json = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Invalid token header. Token string should not contain spaces.")
    
    
    def test_token_authentication_with_different_authorization_header(self):
        url = reverse("my_test_view")
        self.client.credentials(HTTP_AUTHORIZATION="Test %s" % (
            self.refresh_token
        ))

        response = self.client.get(url)
        to_json = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Authentication credentials were not provided.")
        
    
    def test_token_authentication_without_authorization_header(self):
        url = reverse("my_test_view")
        self.client.credentials(HTTP_AUTHORIZATION=" %s" % (
            self.refresh_token
        ))

        response = self.client.get(url)
        to_json = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Authentication credentials were not provided.")
        

    def test_empty_token_authentication(self):
        url = reverse("my_test_view")
        self.client.credentials(HTTP_AUTHORIZATION="%s " % (
            crypto_auth_setting.token_keywoard,
        ))

        response = self.client.get(url)
        to_json = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Invalid token header. No credentials provided.")
    

    def test_token_authentication_with_special_caracteres(self):
        url = reverse("my_test_view")
        self.client.credentials(HTTP_AUTHORIZATION="%s a2ä3" % (
            crypto_auth_setting.token_keywoard,
        ))

        response = self.client.get(url)
        to_json = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Invalid token header. Token string should not contain invalid characters.")
    

    def test_token_authentication_when_user_inactive(self):

        self.user.is_active = False
        self.user.save()

        url = reverse("my_test_view")
        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.token.key
        ))

        response = self.client.get(url)
        to_json = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "User inactive or deleted.")

    
    def test_token_exceed_expiry(self):
        url = reverse("my_test_view")

        self.token.expiry = timezone.now() - timedelta(hours=1)
        self.token.save()

        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.token.key
        ))

        response = self.client.post(url)

        to_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Token expired.")
    

    def test_invalid_token_authentication(self):
        url = reverse("my_test_view")

        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.token.key[:10]
        ))

        response = self.client.post(url)

        to_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Invalid token.")


    @override_settings(CRYPTO_AUTH_MAX_TOKEN_LIMIT=5)
    def test_remove_expired_token_authentication(self):

        self.assertEqual(self.user.auth_crypto.count(), 1)
        url_login = reverse("cryptoAuth_login")
        
        self.client.credentials(HTTP_AUTHORIZATION=get_auth_header(self.username, self.password))

        for _ in range(4):
            self.client.post(url_login)

        self.assertEqual(self.user.auth_crypto.count(), 5)

        for i in self.user.auth_crypto.all():
            i.expiry = timezone.now() - timedelta(hours=1)
            i.save()

        url = reverse("my_test_view")

        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.token.key[:10]
        ))

        response = self.client.post(url)
        to_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(to_json.get("detail"), "Invalid token.")

        self.assertEqual(self.user.auth_crypto.count(), 0)
    

    def test_logout(self):
        url = reverse("cryptoAuth_logout")

        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.token.key
        ))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    @override_settings(CRYPTO_AUTH_MAX_TOKEN_LIMIT=5)
    def test_logout_all(self):
       
        self.assertEqual(self.user.auth_crypto.count(), 1)
        url_login = reverse("cryptoAuth_login")
        
        self.client.credentials(HTTP_AUTHORIZATION=get_auth_header(self.username, self.password))

        for _ in range(4):
            self.client.post(url_login)

        self.assertEqual(self.user.auth_crypto.count(), 5)

        url = reverse("cryptoAuth_logout_all")

        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.token.key
        ))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        
    
    def test_update_token(self):
    
        url = reverse("cryptoAuth_login_update")
        self.client.credentials(HTTP_AUTHORIZATION="%s %s" % (
            crypto_auth_setting.token_keywoard,
            self.refresh_token
        ))

        response = self.client.put(url)
        to_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.assertRaises(Http404):
            get_object_or_404(CryptoToken, key=self.token.key)
