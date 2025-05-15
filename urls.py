from django.urls import path

from .views import LoginView, LogoutAllView, LogoutView, UpdateLoginView

urlpatterns = [
    path('login', LoginView.as_view(), name="cryptoAuth_login"),
    path('login/update', UpdateLoginView.as_view(), name="cryptoAuth_login_update"),
    path('logout', LogoutView.as_view(), name="cryptoAuth_logout"),
    path('logout/all', LogoutAllView.as_view(), name="cryptoAuth_logout_all"),
]
