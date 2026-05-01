# django_crypto_auth

## Documentation:

[django_crypto_auth Documentation](https://docs.mhcode.xyz)

## Django Rest - Token Based Authentication

# Response:

If user is successfully authenticated, response will return a JSON:
    
    {
        "token": "token",
        "expiry": n,
        "refresh_token": "refresh token,
        "user": "username"
    }
    

# Settings:

    - CRYPTO_AUTH_TOKEN_SHUFFLE: tuple | list *
        - Items have to be string letters from "a" to "j"
        - The order will determine how the token will be encrypted
        - You can use the management command `python manage.py create_crypto_shuffle` to automate this.

    - CRYPTO_AUTH_TOKEN_SERIALIZER: string
        - Override django_crypto_auth Serializer
        - Format should be -> "myapp.serializer.SerializerClass"

    - CRYPTO_AUTH_TOKEN_KEYWORD: str
        - Header keyword authentication
        - Default = "TSESSION"

    - CRYPTO_AUTH_MAX_TOKEN_LIMIT: int
        - Max token limit per user
        - Default = 2

    - CRYPTO_AUTH_SUBSET_LENGTH: int
        - Subset from Token
        - Has to be between 2 and 15
        - Default = 4

    - CRYPTO_AUTH_TOKEN_EXPIRY: dict - tuple = ("<keyword>", n: int)
        - keyword should be:
            - seconds, minutes, hours, days or weeks
        - Default = ("minutes", 3)


# Performance & Maintenance:

### Autonomous Cleanup
The module manages its own storage. Expired tokens are automatically deleted every **5 minutes** using a non-blocking cache coordination (Django Cache). This ensures high performance without the need for external tasks like Celery.

### Scalability Optimization
Authentication lookups are performed using **Database Regex + Prefix Indexing**, ensuring O(1) performance even with thousands of active sessions.

# Management Commands:

### `create_crypto_shuffle`
Automates the generation of a randomized `CRYPTO_AUTH_TOKEN_SHUFFLE` and appends it to your `settings.py`.

```bash
python manage.py create_crypto_shuffle
```

## Note:

_LoginVIew_ from *crypto_auth.views* use DEFAULT_AUTHENTICATION_CLASSES from rest_framework.

More info [Here.](https://www.django-rest-framework.org/api-guide/authentication/#api-reference)

if you want to override it, just do
    
    class CustomView(LoginView):
        authentication_classes = [CustomAuthentication]

More info [Here.](https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication)

# Test

    $ python manage.py test django_crypto_auth
