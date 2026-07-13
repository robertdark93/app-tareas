from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import LoginLog

LOCKOUT_ATTEMPTS = 5
LOCKOUT_MINUTES = 2


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _is_locked_out(username):
    since = timezone.now() - timedelta(minutes=LOCKOUT_MINUTES)
    recent = LoginLog.objects.filter(
        username=username, success=False, creado__gte=since
    ).count()
    return recent >= LOCKOUT_ATTEMPTS


def _log_login_attempt(username, ip, success):
    LoginLog.objects.create(username=username, ip_address=ip, success=success)


class LockoutAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False, initial=False,
        label='Recordarme por 7 días',
        widget=forms.CheckboxInput(attrs={'class': 'remember-checkbox'}),
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        ip = _get_client_ip(self.request)

        if username and _is_locked_out(username):
            _log_login_attempt(username, ip, False)
            raise ValidationError(
                f'Demasiados intentos fallidos. Espera {LOCKOUT_MINUTES} minutos e intenta de nuevo.'
            )

        if username and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                _log_login_attempt(username, ip, False)
                raise self.get_invalid_login_error()
            else:
                _log_login_attempt(username, ip, True)
                LoginLog.objects.filter(username=username, success=False).delete()

        return self.cleaned_data
