from .models import Notification, Profile


def notificaciones(request):
    ctx = {}
    if request.user.is_authenticated:
        ctx['notificaciones_no_leidas'] = Notification.objects.filter(
            usuario=request.user, leido=False
        ).count()
        profile, _ = Profile.objects.get_or_create(usuario=request.user)
        ctx['user_rol'] = profile.rol
        ctx['user_es_admin'] = profile.rol == 'admin'
        ctx['user_es_moderador'] = profile.rol == 'moderador'
    else:
        ctx['notificaciones_no_leidas'] = 0
        ctx['user_rol'] = ''
        ctx['user_es_admin'] = False
        ctx['user_es_moderador'] = False
    return ctx
