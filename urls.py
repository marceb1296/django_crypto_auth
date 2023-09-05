from django.urls import path, re_path, include
from django.views.generic import TemplateView
from .views import LoginView, LogoutView, LogoutAllView, UpdateLoginView

urlpatterns = [
    path('login', LoginView.as_view(), name="cryptoAuth_login"),
    path('login/update', UpdateLoginView.as_view(), name="cryptoAuth_login_update"),
    path('logout', LogoutView.as_view(), name="cryptoAuth_logout"),
    path('logout/all', LogoutAllView.as_view(), name="cryptoAuth_logout_all"),
]
