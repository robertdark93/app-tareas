import threading
import time
from datetime import timedelta

from django.apps import AppConfig
from django.conf import settings
from django.db import transaction
from django.utils import timezone


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        import core.signals
        self._start_backup_scheduler()

    def _start_backup_scheduler(self):
        t = threading.Thread(target=self._backup_loop, daemon=True)
        t.start()

    def _backup_loop(self):
        time.sleep(30)
        while True:
            try:
                from django.core.management import call_command
                from .models import BackupConfig
                with transaction.atomic():
                    config = BackupConfig.objects.select_for_update().first()
                    if config and config.auto_backup:
                        need_backup = False
                        if not config.last_backup:
                            need_backup = True
                        else:
                            delta = timedelta(hours=config.interval_hours)
                            if timezone.now() - config.last_backup >= delta:
                                need_backup = True
                        if need_backup:
                            call_command('backup_tareas')
                            config.last_backup = timezone.now()
                            config.save(update_fields=['last_backup'])
                            backup_dir = settings.BASE_DIR / 'backups'
                            from .views import _prune_old_backups
                            _prune_old_backups(backup_dir, config.keep_last)
            except Exception:
                pass
            time.sleep(3600)
