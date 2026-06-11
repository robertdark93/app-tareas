import os
import secrets

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Rota la SECRET_KEY en el archivo .env'

    def handle(self, *args, **options):
        env_path = settings.BASE_DIR / '.env'
        if not env_path.exists():
            self.stderr.write('No se encontró .env')
            return

        new_key = secrets.token_urlsafe(50)
        with open(env_path, 'r') as f:
            lines = f.readlines()

        found = False
        new_lines = []
        for line in lines:
            if line.startswith('DJANGO_SECRET_KEY='):
                new_lines.append(f'DJANGO_SECRET_KEY={new_key}\n')
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f'DJANGO_SECRET_KEY={new_key}\n')

        with open(env_path, 'w') as f:
            f.writelines(new_lines)

        self.stdout.write(self.style.SUCCESS(f'✅ SECRET_KEY rotada: {new_key[:20]}...'))
        self.stdout.write(self.style.WARNING('⚠️  Las sesiones existentes quedarán inválidas.'))