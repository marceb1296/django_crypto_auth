# crypto_auth

## Documentation:

[crypto_auth Documentation](https://docs.mhcode.xyz)

## Django Rest - Token Based Authentication

# Response:

If user is succesfully authenticated, response will return a JSON:
    
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
        - You can use create_token_shuffle method from crypto_auth.helper to generate one

    - CRYPTO_AUTH_TOKEN_MODEL: str
        - Token model to use
        - Default = "crypto_auth.CryptoToken"
        - If override it, model needs to have the field "key" and the attributes:
            - get_expiry -> time in seconds, ex. 180
            - get_refresh_token -> refresh token

    - CRYPTO_AUTH_TOKEN_KEYWOARD: str
        - Header keywoard authentication
        - Default = "TSESSION"

    - CRYPTO_AUTH_MAX_TOKEN_LIMIT: int
        - Max token limit per user
        - Default = 2

    - CRYPTO_AUTH_SUBSET_LENGTH: int
        - Subset from Token
        - Has to be bettwen 2 and 15
        - Default = 4

    - CRYPTO_AUTH_TOKEN_EXPIRY: dict - tuple = ("<keywoard>": n: int)
        - keywoard should be:
            - seconds, minutes, hours, days or weeks
        - Default = ("minutes": 3)


# Serializer:

if you want to override it, needs to be done in a view, ex.

    # views.py
    from crypto_auth.views import LoginView

    class CustomView(LoginView):
        serializer = CustomSerializer


    # urls.py
    ...
    path("route", CustomView.as_view()),
    ...

## Note:

_LoginVIew_ from *crypto_auth.views* use DEFAULT_AUTHENTICATION_CLASSES from rest_framework.

More info [Here.](https://www.django-rest-framework.org/api-guide/authentication/#api-reference)

if you want to override it, just do
    
    class CustomView(LoginView):
        authentication_classes = [CustomAuthentication]

More info [Here.](https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication)

# Test

    # go to crypto_auth
    $ cd crypto_auth

    # move to test branch
    $ git checkout test

    # go back and run
    $ cd ..
    $ python manage.py test crypto_auth
