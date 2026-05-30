import shutil
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Copia db.sqlite3 a backups/ con marca de tiempo"

    def handle(self, *args, **options):
        db_path = settings.DATABASES["default"]["NAME"]
        if not isinstance(db_path, Path):
            db_path = Path(db_path)

        backup_dir = Path(settings.BASE_DIR) / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"db_{timestamp}.sqlite3"

        shutil.copy2(db_path, backup_path)
        self.stdout.write(self.style.SUCCESS(f"Backup creado: {backup_path}"))
