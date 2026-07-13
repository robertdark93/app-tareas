import io
import tempfile
import uuid
from datetime import date, datetime
from pathlib import Path

from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.management import call_command
from django.conf import settings

from .models import (
    Task, Tag, Profile, Note, Department, BackupConfig,
    Notification, TaskTemplate, TaskComment, TaskLog, LoginLog,
    PasswordHistory, AdminLog, TaskWatcher, Attachment,
)


class TestUserMixin:
    def setUp(self):
        self.client = Client()
        self.password = 'testpassword123'
        self.user = User.objects.create_user(
            username='testuser', password=self.password,
            email='test@example.com', first_name='Test', last_name='User',
        )
        self.user2 = User.objects.create_user(
            username='otheruser', password=self.password,
        )
        self.admin_user = User.objects.create_superuser(
            username='admin', password=self.password, email='admin@example.com',
        )


# ==============================================================================
#  MODEL TESTS
# ==============================================================================

class TaskModelTests(TestUserMixin, TestCase):
    def test_task_creation_with_all_fields(self):
        dept = Department.objects.create(nombre='TI', descripcion='Tecnología')
        task = Task.objects.create(
            usuario=self.user,
            creado_por=self.user,
            titulo='Test task',
            comentarios='Some comments',
            estado='pendiente',
            prioridad='urgente',
            departamento=dept,
            fecha_vencimiento=date(2025, 12, 31),
            horas_estimadas=8.5,
            horas_tomadas=7.25,
            recurrente=True,
            frecuencia='semanal',
            orden=1,
        )
        tag = Tag.objects.create(usuario=self.user, nombre='bug', color='#ff0000')
        task.etiquetas.add(tag)
        task.refresh_from_db()

        self.assertEqual(task.usuario, self.user)
        self.assertEqual(task.creado_por, self.user)
        self.assertEqual(task.titulo, 'Test task')
        self.assertEqual(task.comentarios, 'Some comments')
        self.assertEqual(task.estado, 'pendiente')
        self.assertEqual(task.prioridad, 'urgente')
        self.assertEqual(task.departamento, dept)
        self.assertEqual(task.fecha_vencimiento, date(2025, 12, 31))
        self.assertEqual(task.horas_estimadas, 8.5)
        self.assertEqual(task.horas_tomadas, 7.25)
        self.assertTrue(task.recurrente)
        self.assertEqual(task.frecuencia, 'semanal')
        self.assertEqual(task.orden, 1)
        self.assertIsNotNone(task.fecha_creacion)
        self.assertIsNotNone(task.creado)
        self.assertIsNotNone(task.actualizado)
        self.assertEqual(task.etiquetas.count(), 1)
        self.assertEqual(task.etiquetas.first().nombre, 'bug')

    def test_task_estados_choices(self):
        task = Task.objects.create(usuario=self.user, titulo='Estado test')
        valid_estados = {choice[0] for choice in Task.ESTADOS}
        self.assertIn(task.estado, valid_estados)
        self.assertEqual(task.estado, 'pendiente')
        self.assertEqual(task.get_estado_display(), 'Pendiente')

    def test_task_priorities(self):
        task = Task.objects.create(usuario=self.user, titulo='Priority test')
        valid_priorities = {choice[0] for choice in Task.PRIORIDADES}
        self.assertIn(task.prioridad, valid_priorities)
        self.assertEqual(task.prioridad, 'media')

    def test_task_str(self):
        task = Task.objects.create(usuario=self.user, titulo='Mi tarea')
        self.assertEqual(str(task), 'Mi tarea')

    def test_task_get_absolute_url(self):
        task = Task.objects.create(usuario=self.user, titulo='Detail test')
        self.assertEqual(task.get_absolute_url(), f'/tasks/{task.pk}/')


class TagModelTests(TestUserMixin, TestCase):
    def test_tag_creation_with_user(self):
        tag = Tag.objects.create(usuario=self.user, nombre='urgente', color='#ff0000')
        self.assertEqual(tag.usuario, self.user)
        self.assertEqual(tag.nombre, 'urgente')
        self.assertEqual(tag.color, '#ff0000')
        self.assertEqual(str(tag), 'urgente')

    def test_tag_unique_together(self):
        Tag.objects.create(usuario=self.user, nombre='bug')
        with self.assertRaises(Exception):
            Tag.objects.create(usuario=self.user, nombre='bug')

    def test_tag_same_name_different_users(self):
        Tag.objects.create(usuario=self.user, nombre='bug')
        Tag.objects.create(usuario=self.user2, nombre='bug')
        self.assertEqual(Tag.objects.count(), 2)


class ProfileModelTests(TestUserMixin, TestCase):
    def test_profile_auto_creation_via_signal(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)
        self.assertEqual(self.user.profile.rol, 'usuario')

    def test_superuser_gets_admin_role(self):
        profile = self.admin_user.profile
        self.assertEqual(profile.rol, 'admin')

    def test_profile_str(self):
        self.assertEqual(str(self.user.profile), 'testuser - Usuario')


class BackupConfigModelTests(TestCase):
    def test_default_values(self):
        config = BackupConfig.objects.create()
        self.assertFalse(config.auto_backup)
        self.assertEqual(config.interval_hours, 24)
        self.assertEqual(config.keep_last, 10)
        self.assertIsNone(config.last_backup)
        self.assertIn('24h', str(config))
        self.assertIn('10', str(config))

    def test_custom_values(self):
        config = BackupConfig.objects.create(
            auto_backup=True, interval_hours=12, keep_last=5,
        )
        self.assertTrue(config.auto_backup)
        self.assertEqual(config.interval_hours, 12)
        self.assertEqual(config.keep_last, 5)


class DepartmentModelTests(TestCase):
    def test_department_creation(self):
        dept = Department.objects.create(nombre='RRHH', descripcion='Recursos Humanos')
        self.assertEqual(str(dept), 'RRHH')
        self.assertEqual(dept.descripcion, 'Recursos Humanos')


class NoteModelTests(TestUserMixin, TestCase):
    def test_note_creation(self):
        note = Note.objects.create(usuario=self.user, titulo='Mi nota', contenido='Contenido')
        self.assertEqual(str(note), 'Mi nota')
        self.assertEqual(note.get_absolute_url(), f'/notes/{note.pk}/')
        self.assertIsNotNone(note.fecha_creacion)


class NotificationModelTests(TestUserMixin, TestCase):
    def test_notification_creation(self):
        task = Task.objects.create(usuario=self.user, titulo='Notif test')
        notif = Notification.objects.create(usuario=self.user, tarea=task, mensaje='Test message')
        self.assertEqual(str(notif), 'Test message')
        self.assertFalse(notif.leido)


class TaskTemplateModelTests(TestUserMixin, TestCase):
    def test_template_creation(self):
        tpl = TaskTemplate.objects.create(
            usuario=self.user, nombre='Mi plantilla', titulo='Tarea genérica',
            prioridad='alta', recurrente=True, frecuencia='diaria',
        )
        self.assertEqual(str(tpl), 'Mi plantilla')


class TaskCommentModelTests(TestUserMixin, TestCase):
    def test_comment_creation(self):
        task = Task.objects.create(usuario=self.user, titulo='Comment test')
        comment = TaskComment.objects.create(
            tarea=task, usuario=self.user, contenido='Un comentario',
        )
        self.assertIn('Un comentario', str(comment))


class TaskLogModelTests(TestUserMixin, TestCase):
    def test_log_creation(self):
        task = Task.objects.create(usuario=self.user, titulo='Log test')
        log = TaskLog.objects.create(tarea=task, usuario=self.user, accion='creada')
        self.assertIn('Creada', str(log))


class LoginLogModelTests(TestCase):
    def test_login_log_creation(self):
        log = LoginLog.objects.create(username='testuser', ip_address='127.0.0.1', success=True)
        self.assertTrue(log.success)
        self.assertEqual(log.username, 'testuser')


class PasswordHistoryModelTests(TestUserMixin, TestCase):
    def test_password_history(self):
        ph = PasswordHistory.objects.create(usuario=self.user, password='hashed_pw')
        self.assertEqual(str(ph), f'testuser - {ph.creado}')


class AdminLogModelTests(TestUserMixin, TestCase):
    def test_admin_log(self):
        log = AdminLog.objects.create(usuario=self.user, accion='backup', detalle='Test backup')
        self.assertIn('Copia de seguridad', str(log))


class TaskWatcherModelTests(TestUserMixin, TestCase):
    def test_watcher_creation(self):
        task = Task.objects.create(usuario=self.user, titulo='Watch test')
        watcher = TaskWatcher.objects.create(usuario=self.user2, tarea=task)
        self.assertIn('otheruser', str(watcher))


class AttachmentModelTests(TestUserMixin, TestCase):
    def test_attachment_creation(self):
        task = Task.objects.create(usuario=self.user, titulo='Attach test')
        attach = Attachment.objects.create(
            tarea=task, nombre='test.txt',
            archivo='archivos/test.txt',
        )
        self.assertEqual(str(attach), 'test.txt')


# ==============================================================================
#  VIEW TESTS
# ==============================================================================

class LoginViewTests(TestUserMixin, TestCase):
    def test_login_page_loads(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_login_invalid_credentials(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser', 'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')

    def test_login_valid_credentials(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser', 'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_login_redirects_authenticated(self):
        self.client.login(username='testuser', password=self.password)
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)


class ProtectedViewTests(TestUserMixin, TestCase):
    def _assert_redirects_to_login(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_task_list_requires_login(self):
        self._assert_redirects_to_login('/tasks/')

    def test_kanban_requires_login(self):
        self._assert_redirects_to_login('/kanban/')

    def test_calendar_requires_login(self):
        self._assert_redirects_to_login('/calendar/')

    def test_summary_requires_login(self):
        self._assert_redirects_to_login('/summary/')

    def test_notifications_requires_login(self):
        self._assert_redirects_to_login('/notifications/')

    def test_tags_requires_login(self):
        self._assert_redirects_to_login('/tags/')

    def test_notes_requires_login(self):
        self._assert_redirects_to_login('/notes/')

    def test_profile_requires_login(self):
        self._assert_redirects_to_login('/profile/')

    def test_workload_requires_login(self):
        self._assert_redirects_to_login('/workload/')

    def test_home_requires_login(self):
        self._assert_redirects_to_login('/')

    def test_admin_panel_requires_login(self):
        self._assert_redirects_to_login('/admin-panel/')


class AuthenticatedViewTests(TestUserMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password=self.password)

    def test_task_list_page(self):
        Task.objects.create(usuario=self.user, titulo='Task A')
        Task.objects.create(usuario=self.user, titulo='Task B')
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task A')
        self.assertContains(response, 'Task B')

    def test_task_detail_own_task(self):
        task = Task.objects.create(usuario=self.user, titulo='My task', comentarios='Details')
        response = self.client.get(f'/tasks/{task.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My task')
        self.assertContains(response, 'Details')

    def test_task_detail_other_user_task_not_visible(self):
        task = Task.objects.create(usuario=self.user2, titulo='Other task')
        response = self.client.get(f'/tasks/{task.pk}/')
        self.assertEqual(response.status_code, 404)

    def test_kanban_page(self):
        Task.objects.create(usuario=self.user, titulo='Kanban task')
        response = self.client.get('/kanban/')
        self.assertEqual(response.status_code, 200)

    def test_calendar_page(self):
        response = self.client.get('/calendar/')
        self.assertEqual(response.status_code, 200)

    def test_summary_page(self):
        response = self.client.get('/summary/')
        self.assertEqual(response.status_code, 200)

    def test_notification_page(self):
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)

    def test_tags_page(self):
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)

    def test_notes_page(self):
        response = self.client.get('/notes/')
        self.assertEqual(response.status_code, 200)

    def test_profile_page(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_help_page(self):
        response = self.client.get('/help/')
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)

    @override_settings(CHANNEL_LAYERS={'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}})
    def test_task_create_via_post(self):
        data = {
            'titulo': 'New task from test',
            'comentarios': 'Test comments',
            'prioridad': 'alta',
            'usuario': self.user.pk,
        }
        response = self.client.post('/tasks/create/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.filter(titulo='New task from test').count(), 1)
        task = Task.objects.get(titulo='New task from test')
        self.assertEqual(task.usuario, self.user)
        self.assertEqual(task.creado_por, self.user)
        self.assertEqual(task.prioridad, 'alta')
        self.assertEqual(task.estado, 'pendiente')

    def test_task_create_missing_required_fields(self):
        response = self.client.post('/tasks/create/', {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')


class WorkloadViewTests(TestUserMixin, TestCase):
    def test_workload_requires_admin_or_moderator(self):
        self.client.login(username='testuser', password=self.password)
        response = self.client.get('/workload/')
        self.assertEqual(response.status_code, 403)

    def test_workload_accessible_by_admin(self):
        self.client.login(username='admin', password=self.password)
        self.admin_user.profile.refresh_from_db()
        response = self.client.get('/workload/')
        self.assertEqual(response.status_code, 200)

    def test_workload_accessible_by_moderator(self):
        profile = self.user2.profile
        profile.rol = 'moderador'
        profile.save()
        self.client.login(username='otheruser', password=self.password)
        response = self.client.get('/workload/')
        self.assertEqual(response.status_code, 200)


class AdminViewTests(TestUserMixin, TestCase):
    def test_admin_dashboard_denied_for_normal_user(self):
        self.client.login(username='testuser', password=self.password)
        response = self.client.get('/admin-panel/')
        self.assertEqual(response.status_code, 403)

    def test_admin_dashboard_accessible_by_admin(self):
        self.client.login(username='admin', password=self.password)
        response = self.client.get('/admin-panel/')
        self.assertEqual(response.status_code, 200)


# ==============================================================================
#  URL TESTS
# ==============================================================================

class URLPatternTests(TestCase):
    def test_urls_resolve_correctly(self):
        url_patterns = {
            '/accounts/login/': 'login',
            '/accounts/logout/': 'logout',
            '/': 'index',
            '/profile/': 'profile',
            '/tasks/': 'task_list',
            '/tasks/create/': 'task_create',
            '/calendar/': 'calendar',
            '/tags/': 'tag_list',
            '/tags/create/': 'tag_create',
            '/notes/': 'note_list',
            '/notes/create/': 'note_create',
            '/kanban/': 'kanban',
            '/summary/': 'summary',
            '/export/csv/': 'export_csv',
            '/notifications/': 'notification_list',
            '/workload/': 'workload',
            '/help/': 'help',
            '/about/': 'about',
        }
        for path, expected_name in url_patterns.items():
            with self.subTest(path=path, name=expected_name):
                response = self.client.get(path) if path != '/accounts/logout/' else self.client.post(path)
                self.assertIn(response.status_code, (200, 302, 403))

    def test_named_urls_reverse(self):
        tests = [
            ('login', {}, '/accounts/login/'),
            ('logout', {}, '/accounts/logout/'),
            ('index', {}, '/'),
            ('profile', {}, '/profile/'),
            ('task_list', {}, '/tasks/'),
            ('task_create', {}, '/tasks/create/'),
            ('calendar', {}, '/calendar/'),
            ('tag_list', {}, '/tags/'),
            ('tag_create', {}, '/tags/create/'),
            ('note_list', {}, '/notes/'),
            ('note_create', {}, '/notes/create/'),
            ('kanban', {}, '/kanban/'),
            ('summary', {}, '/summary/'),
            ('export_csv', {}, '/export/csv/'),
            ('notification_list', {}, '/notifications/'),
            ('workload', {}, '/workload/'),
            ('help', {}, '/help/'),
            ('about', {}, '/about/'),
        ]
        for name, kwargs, expected in tests:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                self.assertEqual(url, expected)

    def test_pk_urls_resolve(self):
        tests = [
            ('task_detail', {'pk': 1}, '/tasks/1/'),
            ('task_update', {'pk': 1}, '/tasks/1/update/'),
            ('task_delete', {'pk': 1}, '/tasks/1/delete/'),
            ('task_complete', {'pk': 1}, '/tasks/1/complete/'),
            ('tag_delete', {'pk': 1}, '/tags/1/delete/'),
            ('note_detail', {'pk': 1}, '/notes/1/'),
            ('note_update', {'pk': 1}, '/notes/1/update/'),
            ('note_delete', {'pk': 1}, '/notes/1/delete/'),
            ('notification_read', {'pk': 1}, '/notifications/1/read/'),
            ('watch_task', {'pk': 1}, '/tasks/1/watch/'),
            ('unwatch_task', {'pk': 1}, '/tasks/1/unwatch/'),
            ('task_lock', {'pk': 1}, '/tasks/1/lock/'),
            ('task_unlock', {'pk': 1}, '/tasks/1/unlock/'),
            ('task_change_status', {'pk': 1}, '/tasks/1/change-status/'),
        ]
        for name, kwargs, expected in tests:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                self.assertEqual(url, expected)

    def test_uuid_url_resolves(self):
        token = uuid.uuid4()
        url = reverse('shared_task', kwargs={'token': token})
        self.assertEqual(url, f'/shared/{token}/')


class AdditionalModelAndSignalTests(TestUserMixin, TestCase):
    def test_profile_departments(self):
        dept = Department.objects.create(nombre='Ventas')
        self.user.profile.departamento = dept
        self.user.profile.departamentos.add(dept)
        self.user.profile.save()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.departamento, dept)
        self.assertIn(dept, self.user.profile.departamentos.all())

    def test_task_subtask_relation(self):
        parent = Task.objects.create(usuario=self.user, titulo='Parent')
        child = Task.objects.create(usuario=self.user, titulo='Child', parent=parent)
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.subtareas.all())


# ==============================================================================
#  COMMAND TESTS
# ==============================================================================

class BackupCommandTests(TestCase):
    def test_backup_tareas_command_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'test_db.sqlite3'
            db_path.touch()
            with override_settings(
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': str(db_path),
                    }
                },
                BASE_DIR=Path(tmpdir),
            ):
                out = io.StringIO()
                call_command('backup_tareas', stdout=out)
                self.assertIn('Respaldo creado', out.getvalue())

    def test_backup_tareas_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'test_db.sqlite3'
            db_path.touch()
            with override_settings(
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': str(db_path),
                    }
                },
                BASE_DIR=Path(tmpdir),
            ):
                out = io.StringIO()
                result = call_command('backup_tareas', stdout=out)
                self.assertIn('Respaldo creado', out.getvalue())
                backup_dir = Path(tmpdir) / 'backups'
                self.assertTrue(backup_dir.exists())
                backups = list(backup_dir.iterdir())
                self.assertEqual(len(backups), 1)
                self.assertIn('db_', backups[0].name)
