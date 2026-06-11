from django.contrib import admin
from .models import Task, Note, Notification, Tag, Attachment, Department, Profile, TaskTemplate, TaskComment, TaskLog, LoginLog


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'departamento']
    list_filter = ['rol', 'departamento']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'usuario', 'color']
    list_filter = ['usuario']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'departamento', 'estado', 'prioridad', 'fecha_creacion']
    list_filter = ['estado', 'prioridad', 'recurrente', 'departamento']
    search_fields = ['titulo', 'comentarios']
    filter_horizontal = ['etiquetas']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tarea', 'subido']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'fecha_creacion']
    search_fields = ['titulo', 'contenido']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['mensaje', 'usuario', 'leido', 'creado']
    list_filter = ['leido', 'creado']


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'usuario', 'prioridad', 'recurrente']
    list_filter = ['prioridad', 'recurrente']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['tarea', 'usuario', 'creado']
    list_filter = ['creado']


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ['tarea', 'usuario', 'accion', 'creado']
    list_filter = ['accion', 'creado']


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['username', 'ip_address', 'success', 'creado']
    list_filter = ['success', 'creado']
    search_fields = ['username', 'ip_address']
