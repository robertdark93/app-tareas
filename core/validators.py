import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplexityValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _('La contraseña debe tener al menos 8 caracteres.'),
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos una letra mayúscula.'),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos una letra minúscula.'),
                code='password_no_lower',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos un número.'),
                code='password_no_digit',
            )
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?`~]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos un carácter especial (!@#$%...).'),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            'La contraseña debe tener al menos 8 caracteres, '
            'incluir mayúsculas, minúsculas, números y un carácter especial.'
        )


class PasswordHistoryValidator:
    def validate(self, password, user=None):
        if user is None:
            return
        from .models import PasswordHistory
        history = PasswordHistory.objects.filter(usuario=user).order_by('-creado')[:5]
        for entry in history:
            from django.contrib.auth.hashers import check_password
            if check_password(password, entry.password):
                raise ValidationError(
                    _('No puedes reutilizar una de tus últimas 5 contraseñas.'),
                    code='password_reused',
                )

    def get_help_text(self):
        return _('No puedes reutilizar ninguna de tus últimas 5 contraseñas.')
