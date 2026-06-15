from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (Task, Note, Tag, Department, Profile,
                     TaskComment, TaskTemplate)


class TaskCreateForm(forms.ModelForm):
    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(), label='Asignar a',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    etiquetas = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(), label='Etiquetas',
        required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )
    archivos = forms.FileField(
        label='Adjuntar archivos', required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Task
        fields = ['titulo', 'comentarios', 'prioridad', 'departamento',
                  'horas_estimadas', 'fecha_vencimiento', 'recordatorio',
                  'recurrente', 'frecuencia', 'parent', 'usuario']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/AAAA', 'autocomplete': 'off'}, format='%d/%m/%Y'),
            'recordatorio': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/AAAA HH:MM', 'autocomplete': 'off'}, format='%d/%m/%Y %H:%M'),
            'comentarios': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'horas_estimadas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'recurrente': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        usuario_actual = kwargs.pop('usuario_actual', None)
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if usuario_actual:
            u = User.objects.get(pk=usuario_actual)
            self.fields['etiquetas'].queryset = Tag.objects.filter(usuario=u)
            self.fields['parent'].queryset = Task.objects.filter(usuario=u)
            if not self.instance.pk:
                self.fields['usuario'].initial = usuario_actual
        self.fields['departamento'].queryset = Department.objects.all()


class TaskUpdateForm(forms.ModelForm):
    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(), label='Asignar a',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    etiquetas = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(), label='Etiquetas',
        required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )
    archivos = forms.FileField(
        label='Adjuntar archivos', required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Task
        fields = ['titulo', 'comentarios', 'estado', 'prioridad', 'departamento',
                  'horas_estimadas', 'fecha_vencimiento', 'horas_tomadas', 'recordatorio',
                  'recurrente', 'frecuencia', 'parent', 'usuario']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/AAAA', 'autocomplete': 'off'}, format='%d/%m/%Y'),
            'recordatorio': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/AAAA HH:MM', 'autocomplete': 'off'}, format='%d/%m/%Y %H:%M'),
            'comentarios': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'horas_estimadas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'horas_tomadas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'recurrente': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['departamento'].queryset = Department.objects.all()
        if self.instance and self.instance.pk:
            user = self.instance.usuario
            self.fields['etiquetas'].queryset = Tag.objects.filter(usuario=user)
            self.fields['parent'].queryset = Task.objects.filter(usuario=user).exclude(pk=self.instance.pk)
            self.fields['etiquetas'].initial = self.instance.etiquetas.all()


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['titulo', 'contenido']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Escribe un comentario...'}),
        }
        labels = {'contenido': ''}


class TaskTemplateForm(forms.ModelForm):
    class Meta:
        model = TaskTemplate
        fields = ['nombre', 'titulo', 'comentarios', 'prioridad', 'horas_estimadas', 'recurrente', 'frecuencia']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'comentarios': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'horas_estimadas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'recurrente': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
        }


# ---- Admin Forms ----

class AdminUserCreateForm(forms.Form):
    username = forms.CharField(label='Usuario', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Correo', required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='Nombre', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Apellidos', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    rol = forms.ChoiceField(label='Rol', choices=Profile.ROLES, widget=forms.Select(attrs={'class': 'form-control'}))
    departamentos = forms.ModelMultipleChoiceField(
        label='Departamentos', queryset=Department.objects.all(), required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '6'}),
    )

    def clean_password(self):
        p = self.cleaned_data.get('password')
        if p:
            validate_password(p)
        return p


class AdminUserEditForm(forms.Form):
    email = forms.EmailField(label='Correo', required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='Nombre', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Apellidos', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(label='Activo', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))
    rol = forms.ChoiceField(label='Rol', choices=Profile.ROLES, widget=forms.Select(attrs={'class': 'form-control'}))
    departamentos = forms.ModelMultipleChoiceField(
        label='Departamentos', queryset=Department.objects.all(), required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '6'}),
    )
    nueva_password = forms.CharField(label='Nueva contraseña', required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class AdminDepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class ProfileForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Nueva contraseña', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dejar vacío para no cambiar'}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repite la contraseña'}),
    )
    avatar = forms.ImageField(
        label='Subir foto', required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
    )
    eliminar_avatar = forms.BooleanField(
        label='Eliminar foto', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError('La imagen no puede superar los 2 MB.')
        return avatar

    def clean_password1(self):
        p1 = self.cleaned_data.get('password1')
        if p1:
            validate_password(p1)
        return p1

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned
