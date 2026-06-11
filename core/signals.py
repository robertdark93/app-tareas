from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, **kwargs):
    Profile.objects.get_or_create(usuario=instance)


@receiver(post_migrate)
def crear_datos_default(sender, **kwargs):
    if sender.name == 'core':
        user, created = User.objects.get_or_create(username='hades')
        if created:
            user.set_password('Death123*')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        profile, _ = Profile.objects.get_or_create(usuario=user)
        if profile.rol != 'admin':
            profile.rol = 'admin'
            profile.save()
