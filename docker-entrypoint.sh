#!/bin/bash
set -e

# Esperar a PostgreSQL si estamos usando Docker
if [ -n "$DB_HOST" ]; then
    echo "Esperando a PostgreSQL..."
    if command -v pg_isready &>/dev/null; then
        until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" 2>/dev/null; do
            sleep 1
        done
    else
        until python -c "
import psycopg2, os, time
try:
    psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT', 5432),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        dbname=os.environ.get('DB_NAME')
    )
    print('ok', end='')
except Exception:
    exit(1)
" 2>/dev/null; do
            sleep 1
        done
    fi
    echo "PostgreSQL listo."
fi

# Migraciones
python manage.py migrate --noinput

# Colectar archivos estáticos (para producción con WhiteNoise)
python manage.py collectstatic --noinput 2>&1 | grep -v '^$'

# Crear superusuario si no existe
python manage.py shell -c "
from django.contrib.auth.models import User
from core.models import Profile
username = '$DJANGO_SUPERUSER_USERNAME'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    u = User.objects.get(username=username)
    Profile.objects.get_or_create(usuario=u, defaults={'rol': 'admin'})
    print(f'Superusuario \"{username}\" creado.')
else:
    u = User.objects.get(username=username)
    Profile.objects.get_or_create(usuario=u, defaults={'rol': 'admin'})
    print(f'Superusuario \"{username}\" ya existe.')
"

mkdir -p /app/media/avatars /app/backups 2>/dev/null || true

exec daphne -b 0.0.0.0 -p 5006 tareas_project.asgi:application
