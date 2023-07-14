from django.urls import path, re_path, include
from django.views.generic import TemplateView
from .views import LoginView, LogoutView, LogoutAllView, MyTestView, UpdateLoginView

urlpatterns = [
    path('login', LoginView.as_view(), name="cryptoAuth_login"),
    path('login/update', UpdateLoginView.as_view(), name="cryptoAuth_login_update"),
    path('logout', LogoutView.as_view(), name="cryptoAuth_logout"),
    path('logout/all', LogoutAllView.as_view(), name="cryptoAuth_logout_all"),
    path('test/', MyTestView.as_view(), name="my_test_view"), # Only for test case
]