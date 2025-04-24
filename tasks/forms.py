from django import forms
from django.contrib.auth.models import User
from .models import EmpleadoPerfil, Tienda, Tarea, Evidencia
from .models import Calificacion

class RegistroEmpleadoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    tienda = forms.ModelChoiceField(queryset=Tienda.objects.all(), label="Tienda")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            EmpleadoPerfil.objects.create(
                user=user,
                tienda=self.cleaned_data['tienda'],
                es_jefe=False
            )
        return user


class RegistroJefeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    tienda = forms.ModelChoiceField(queryset=Tienda.objects.all(), label="Tienda a administrar")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            EmpleadoPerfil.objects.create(
                user=user,
                tienda=self.cleaned_data['tienda'],
                es_jefe=True
            )
        return user


class CrearTareaForm(forms.ModelForm):
    empleados = forms.ModelMultipleChoiceField(
        queryset=EmpleadoPerfil.objects.filter(es_jefe=False),
        widget=forms.CheckboxSelectMultiple,
        label="Asignar a empleados"
    )

    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'tiempo_estimado', 'empleados']
        widgets = {
            'tiempo_estimado': forms.TextInput(attrs={'placeholder': 'hh:mm:ss'}),
        }


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Evidencia
        fields = ['comentario', 'foto']

class CalificacionForm(forms.ModelForm):
    puntuacion = forms.IntegerField(min_value=1, max_value=5, label="Puntuación (1–5)")

    class Meta:
        model = Calificacion
        fields = ['puntuacion', 'comentario']