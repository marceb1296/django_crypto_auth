import hashlib
import random
import secrets
from django.core.exceptions import ImproperlyConfigured
import string
from typing import Union, List, Tuple
try:
    from .app_settings import crypto_auth_default_setting, CryptoAuthSettings
except:
    raise ImproperlyConfigured("Missing django_crypto_auth settings")
    

alphabet = string.ascii_lowercase

class CryptoAuthentication(CryptoAuthSettings):

    @property
    def generate_token(self) -> str:
        token = secrets.token_bytes(crypto_auth_default_setting.default_length)
        hash_object = hashlib.sha256(token)
        return hash_object.hexdigest()
    
    
    def token_key(self, key: str, encrypt: bool = False, subset: bool = False,  shuffle: list = []) -> str:
        if encrypt:
            return self._encrypt_key(self._key_int_to_letters(key[0:-1:self.subset_length]), shuffle)           
        if subset: 
            return key[0:-1:self.subset_length]          
        return self._key_int_to_letters(key[0:-1:self.subset_length])
       

    def _key_int_to_letters(self, key: str) -> str:
        return "".join([
            chr(int(i) + 65).lower()
            if i.isdigit() else i
            for i in key 
        ])
    
    
    def _encrypt_key(self, key: str, encrypt: Union[list, Tuple]) -> str:
        _encrypted = ""

        for i in key:
            _encrypted += str(encrypt.index(i))

        return _encrypted
    
    
    def decrypt_key(self, encrypt: str, shuffle: Union[list, Tuple]) -> str:
        _decrypted = ""

        for i in encrypt:
            _decrypted += shuffle[int(i)]
        
        return _decrypted

    
    def verify_key(self, key: str, _key: str) -> bool:
        return key == _key
    

    def combine_key_with_token(self, key:str) -> str:
        
        _token = ""
        _count = 0
        _count_key = 0

        key_length = len(key)
        token = self.generate_token
        max_token_length = len(token)
        
        while True:
            if _count == max_token_length - 1:
                break
            if _count == 0:
                _token += key[_count]
                _count_key += 1
            elif (_count % int(max_token_length / key_length)) == 0:
                _token += key[_count_key]
                _count_key += 1
            else:
                _token += token[_count]
            _count += 1

        return _token

    
    def key(self, key: str) -> str:

        token = self.token_key(key)
        return self._encrypt_key(token, self.get_token_shuffle)

