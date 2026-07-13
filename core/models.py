import uuid

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Department(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    creado = models.DateTimeField(auto_now_add=True, null=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return self.nombre


class Profile(models.Model):
    ROLES = [
        ('admin', 'Administrador'),
        ('moderador', 'Moderador'),
        ('usuario', 'Usuario'),
    ]
    ICONOS = [
        ('', 'Ninguno (inicial del nombre)'),
        ('🧑‍💻', 'Programador'),
        ('👨‍💻', 'Programador hombre'),
        ('👩‍💻', 'Programadora mujer'),
        ('🕵️', 'Detective'),
        ('🧑‍🔧', 'Técnico'),
        ('👨‍🔧', 'Técnico hombre'),
        ('👩‍🔧', 'Técnica mujer'),
        ('🧑‍🚀', 'Astronauta'),
        ('👨‍🚀', 'Astronauta hombre'),
        ('👩‍🚀', 'Astronauta mujer'),
        ('🧑‍🔬', 'Científico'),
        ('👨‍🔬', 'Científico hombre'),
        ('👩‍🔬', 'Científica mujer'),
        ('🧑‍🏫', 'Profesor'),
        ('👨‍🏫', 'Profesor hombre'),
        ('👩‍🏫', 'Profesora mujer'),
        ('🧑‍🎓', 'Estudiante'),
        ('👨‍🎓', 'Estudiante hombre'),
        ('👩‍🎓', 'Estudiante mujer'),
        ('🧑‍🎨', 'Artista'),
        ('👨‍🎨', 'Artista hombre'),
        ('👩‍🎨', 'Artista mujer'),
        ('🧑‍🍳', 'Cocinero'),
        ('👨‍🍳', 'Cocinero hombre'),
        ('👩‍🍳', 'Cocinera mujer'),
        ('🧑‍⚕️', 'Médico'),
        ('👨‍⚕️', 'Médico hombre'),
        ('👩‍⚕️', 'Médica mujer'),
        ('🧑‍✈️', 'Piloto'),
        ('👨‍✈️', 'Piloto hombre'),
        ('👩‍✈️', 'Piloto mujer'),
        ('🧑‍🌾', 'Granjero'),
        ('👨‍🌾', 'Granjero hombre'),
        ('👩‍🌾', 'Granjera mujer'),
        ('🦸', 'Superhéroe'),
        ('🦹', 'Supervillano'),
        ('🧙', 'Mago/Maga'),
        ('🧝', 'Elfo/Elfa'),
        ('🧛', 'Vampiro'),
        ('🧞', 'Genio'),
        ('🧜', 'Sireno/Sirena'),
        ('🎅', 'Santa Claus'),
        ('🤴', 'Príncipe'),
        ('👸', 'Princesa'),
        ('👑', 'Corona'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rol = models.CharField(max_length=10, choices=ROLES, default='usuario', verbose_name='Rol')
    departamento = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Departamento (principal)')
    departamentos = models.ManyToManyField(Department, blank=True, related_name='perfiles',
                                            verbose_name='Departamentos')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Foto de perfil')
    avatar_icon = models.CharField(max_length=20, choices=ICONOS, blank=True, default='',
                                   verbose_name='Icono de perfil')
    creado = models.DateTimeField(auto_now_add=True, null=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f'{self.usuario.username} - {self.get_rol_display()}'


class Tag(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    color = models.CharField(max_length=7, default='#58a6ff', verbose_name='Color')
    creado = models.DateTimeField(auto_now_add=True, null=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ['usuario', 'nombre']
        ordering = ['nombre']
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'

    def __str__(self):
        return self.nombre


class Task(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('proceso', 'En Proceso'),
        ('revision', 'En Revisión'),
        ('terminada', 'Terminada'),
    ]
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    FRECUENCIAS = [
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Responsable')
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='tareas_creadas', verbose_name='Creada por')
    titulo = models.CharField(max_length=200, verbose_name='Título')
    comentarios = models.TextField(blank=True, verbose_name='Comentarios')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', verbose_name='Estado')
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media', verbose_name='Prioridad')
    departamento = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Departamento')
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de vencimiento')
    fecha_completada = models.DateField(null=True, blank=True, verbose_name='Fecha completada')
    horas_estimadas = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Horas estimadas')
    horas_tomadas = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Horas tomadas')
    recordatorio = models.DateTimeField(null=True, blank=True, verbose_name='Recordatorio')
    recurrente = models.BooleanField(default=False, verbose_name='Recurrente')
    frecuencia = models.CharField(max_length=10, choices=FRECUENCIAS, blank=True, verbose_name='Frecuencia')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='subtareas', verbose_name='Tarea padre')
    etiquetas = models.ManyToManyField(Tag, blank=True, verbose_name='Etiquetas')
    share_token = models.UUIDField(editable=False, null=True, blank=True, unique=True,
                                    verbose_name='Token compartir')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    locked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='tareas_bloqueadas', verbose_name='Bloqueada por')
    locked_at = models.DateTimeField(null=True, blank=True, verbose_name='Bloqueada desde')

    class Meta:
        ordering = ['orden', '-fecha_creacion', '-creado']
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('task_detail', args=[str(self.id)])


class Attachment(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='archivos', verbose_name='Tarea')
    archivo = models.FileField(upload_to='archivos/%Y/%m/', verbose_name='Archivo')
    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    subido = models.DateTimeField(auto_now_add=True, verbose_name='Subido')
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-subido']
        verbose_name = 'Archivo adjunto'
        verbose_name_plural = 'Archivos adjuntos'

    def __str__(self):
        return self.nombre


class Note(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    titulo = models.CharField(max_length=200, verbose_name='Título')
    contenido = models.TextField(verbose_name='Contenido')
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de creación')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion', '-creado']
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('note_detail', args=[str(self.id)])


class Notification(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Tarea')
    mensaje = models.CharField(max_length=255, verbose_name='Mensaje')
    leido = models.BooleanField(default=False, verbose_name='Leído')
    creado = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return self.mensaje


class TaskTemplate(models.Model):
    PRIORIDADES = Task.PRIORIDADES
    FRECUENCIAS = Task.FRECUENCIAS

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    nombre = models.CharField(max_length=200, verbose_name='Nombre de plantilla')
    titulo = models.CharField(max_length=200, verbose_name='Título de tarea')
    comentarios = models.TextField(blank=True, verbose_name='Comentarios')
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media', verbose_name='Prioridad')
    horas_estimadas = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Horas estimadas')
    recurrente = models.BooleanField(default=False, verbose_name='Recurrente')
    frecuencia = models.CharField(max_length=10, choices=FRECUENCIAS, blank=True, verbose_name='Frecuencia')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Plantilla de tarea'
        verbose_name_plural = 'Plantillas de tareas'

    def __str__(self):
        return self.nombre


class TaskComment(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_comentarios', verbose_name='Tarea')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    contenido = models.TextField(verbose_name='Comentario')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['creado']
        verbose_name = 'Comentario de tarea'
        verbose_name_plural = 'Comentarios de tareas'

    def __str__(self):
        return f'{self.usuario.username}: {self.contenido[:50]}'


class TaskLog(models.Model):
    ACCIONES = [
        ('creada', 'Creada'),
        ('editada', 'Editada'),
        ('estado', 'Cambio de estado'),
        ('reasignada', 'Reasignada'),
    ]
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='logs', verbose_name='Tarea')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    accion = models.CharField(max_length=20, choices=ACCIONES, verbose_name='Acción')
    detalle = models.TextField(blank=True, verbose_name='Detalle')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Historial de tarea'
        verbose_name_plural = 'Historiales de tareas'

    def __str__(self):
        return f'{self.get_accion_display()} - {self.tarea.titulo}'


class LoginLog(models.Model):
    username = models.CharField(max_length=150, verbose_name='Usuario')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP')
    success = models.BooleanField(default=False, verbose_name='Exitoso')
    creado = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Intento de login'
        verbose_name_plural = 'Intentos de login'

    def __str__(self):
        return f'{self.username} - {"✅" if self.success else "❌"} - {self.creado}'


class PasswordHistory(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password = models.CharField(max_length=128, verbose_name='Hash de contraseña')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Historial de contraseña'
        verbose_name_plural = 'Historial de contraseñas'

    def __str__(self):
        return f'{self.usuario.username} - {self.creado}'


class AdminLog(models.Model):
    ACCIONES = [
        ('crear_usuario', 'Crear usuario'),
        ('editar_usuario', 'Editar usuario'),
        ('eliminar_tarea', 'Eliminar tarea'),
        ('reasignar_masiva', 'Reasignación masiva'),
        ('cambiar_rol', 'Cambiar rol'),
        ('backup', 'Copia de seguridad'),
        ('otro', 'Otro'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Administrador')
    accion = models.CharField(max_length=30, choices=ACCIONES, verbose_name='Acción')
    detalle = models.TextField(blank=True, verbose_name='Detalle')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Bitácora de administración'
        verbose_name_plural = 'Bitácoras de administración'

    def __str__(self):
        return f'{self.usuario.username if self.usuario else "?"} - {self.get_accion_display()} - {self.creado}'


class TaskWatcher(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas_observadas',
                                verbose_name='Usuario')
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='observadores',
                              verbose_name='Tarea')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ['usuario', 'tarea']
        ordering = ['-creado']
        verbose_name = 'Observador de tarea'
        verbose_name_plural = 'Observadores de tareas'

    def __str__(self):
        return f'{self.usuario.username} → {self.tarea.titulo}'


class BackupConfig(models.Model):
    auto_backup = models.BooleanField(default=False, verbose_name='Copias automáticas')
    interval_hours = models.PositiveIntegerField(default=24, verbose_name='Intervalo (horas)')
    keep_last = models.PositiveIntegerField(default=10, verbose_name='Conservar últimas')
    last_backup = models.DateTimeField(null=True, blank=True, verbose_name='Última copia')
    creado = models.DateTimeField(auto_now_add=True, null=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'Configuración de respaldo'
        verbose_name_plural = 'Configuracion de respaldos'

    def __str__(self):
        return f'Backup cada {self.interval_hours}h, guardar {self.keep_last}'


class EmailConfig(models.Model):
    host = models.CharField(max_length=255, blank=True, default='', verbose_name='Servidor SMTP')
    port = models.PositiveIntegerField(default=587, verbose_name='Puerto')
    username = models.CharField(max_length=255, blank=True, default='', verbose_name='Usuario')
    password = models.CharField(max_length=255, blank=True, default='', verbose_name='Contraseña')
    from_email = models.EmailField(max_length=255, blank=True, default='', verbose_name='Correo remitente')
    use_tls = models.BooleanField(default=True, verbose_name='Usar TLS')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración de correo'
        verbose_name_plural = 'Configuración de correo'

    def __str__(self):
        return f'SMTP {self.host}:{self.port}'
