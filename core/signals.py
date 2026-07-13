from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, **kwargs):
    profile, created = Profile.objects.get_or_create(usuario=instance)
    if instance.is_superuser and profile.rol != 'admin':
        profile.rol = 'admin'
        profile.save()

