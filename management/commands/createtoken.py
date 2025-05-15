from django.core.management.base import BaseCommand
from django_crypto_auth.helper import create_token_shuffle


class Command(BaseCommand):
    help = "Create token shuffle for django_crypto_auth"

    def handle(self, *args, **options):
        create_token_shuffle()
