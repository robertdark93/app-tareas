import os
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea respaldo de la base de datos (pg_dump para PostgreSQL, copia para SQLite)"

    def handle(self, *args, **options):
        db_conf = settings.DATABASES["default"]
        backup_dir = Path(settings.BASE_DIR) / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if db_conf["ENGINE"].endswith("postgresql"):
            host = db_conf.get("HOST") or os.environ.get("DB_HOST", "localhost")
            port = db_conf.get("PORT") or os.environ.get("DB_PORT", "5432")
            name = db_conf.get("NAME") or os.environ.get("DB_NAME", "tareas")
            user = db_conf.get("USER") or os.environ.get("DB_USER", "tareas")
            password = db_conf.get("PASSWORD") or os.environ.get("DB_PASSWORD", "tareas")

            backup_path = backup_dir / f"db_{timestamp}.dump"
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            cmd = ["pg_dump", "-Fc", "-h", host, "-p", port, "-U", user, "-d", name, "-f", str(backup_path)]
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode != 0:
                msg = f"Error pg_dump: {result.stderr.strip()}"
                raise RuntimeError(msg)
        else:
            db_path = Path(db_conf["NAME"])
            backup_path = backup_dir / f"db_{timestamp}.sqlite3"
            import shutil
            shutil.copy2(db_path, backup_path)

        self.stdout.write(self.style.SUCCESS(f"Respaldo creado: {backup_path}"))
        return str(backup_path)
