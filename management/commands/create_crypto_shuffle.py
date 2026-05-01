import importlib
import random

from django.conf import settings
from django.core.management.base import BaseCommand

from django_crypto_auth.helper import alphabet


class Command(BaseCommand):
    help = 'Generates a new CRYPTO_AUTH_TOKEN_SHUFFLE and appends it to settings.py'

    def handle(self, *args, **options):
        # 1. Generate the shuffle
        shuffle = list(alphabet[:10])
        random.shuffle(shuffle)

        # 2. Locate settings.py using Django's native settings module
        try:
            settings_module = importlib.import_module(settings.SETTINGS_MODULE)
            settings_path = settings_module.__file__
            if settings_path.endswith(".pyc"):
                settings_path = settings_path[:-1]
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error: Could not locate settings.py file. ({e})")
            )
            return

        # 3. Read current content to check for existence
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading settings.py: {e}"))
            return

        if 'CRYPTO_AUTH_TOKEN_SHUFFLE' in content:
            self.stdout.write(self.style.WARNING("WARNING: CRYPTO_AUTH_TOKEN_SHUFFLE is already defined in settings.py."))
            self.stdout.write(f"Generated shuffle (not added): {shuffle}")
            return

        # 4. Append to the end of the file with a blank line before
        try:
            with open(settings_path, 'a') as f:
                f.write(f"\n\nCRYPTO_AUTH_TOKEN_SHUFFLE = {shuffle}\n")
            
            self.stdout.write(self.style.SUCCESS(f"Successfully generated and added CRYPTO_AUTH_TOKEN_SHUFFLE to {settings_path}"))
            self.stdout.write("\n" + "="*80)
            self.stdout.write(self.style.SUCCESS("IMPORTANTE: Se ha añadido la configuración directamente a settings.py."))
            self.stdout.write(self.style.WARNING("RECOMENDACIÓN: Para mayor seguridad, considera mover este valor a una variable de entorno (.env)."))
            self.stdout.write("="*80 + "\n")
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error writing to settings.py: {e}"))
