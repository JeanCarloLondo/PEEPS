from django import forms
from django.contrib.auth.models import User
from .models import EmpleadoPerfil, Tienda, Tarea, Evidencia
from .models import Calificacion
from .models import Tarea, Evidencia, Calificacion
from .models import TiendaConfiguracion
from datetime import timedelta
import re

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

    prioridad = forms.ChoiceField(choices=Tarea.PRIORIDADES, label="Prioridad")

    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'tiempo_estimado', 'empleados', 'prioridad']
        widgets = {
            'tiempo_estimado': forms.TextInput(attrs={
                'placeholder': 'hh:mm',
                'pattern': '^([0-9]{1,2}):([0-5][0-9])$',
                'title': 'Formato: hh:mm (ejemplo: 02:30 para 2 horas y 30 minutos)'
            }),
        }

    def clean_tiempo_estimado(self):
        tiempo = self.cleaned_data.get('tiempo_estimado')
        
        if isinstance(tiempo, str):
            # Si es una cadena, intentamos convertirla a timedelta
            pattern = re.compile(r'^(\d{1,2}):([0-5]\d)$')
            match = pattern.match(tiempo)
            if not match:
                raise forms.ValidationError('El formato debe ser hh:mm (ejemplo: 02:30)')
            
            horas = int(match.group(1))
            minutos = int(match.group(2))
            
            # Validar que los valores sean razonables
            if horas > 99:
                raise forms.ValidationError('Las horas no pueden ser mayores a 99')
            if minutos > 59:
                raise forms.ValidationError('Los minutos no pueden ser mayores a 59')
            
            # Convertir a timedelta
            return timedelta(hours=horas, minutes=minutos)
        
        elif isinstance(tiempo, timedelta):
            # Si ya es un timedelta, asegurarnos de que solo tenga horas y minutos
            total_seconds = int(tiempo.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            # Validar que los valores sean razonables
            if hours > 99:
                raise forms.ValidationError('Las horas no pueden ser mayores a 99')
            
            # Crear un nuevo timedelta solo con horas y minutos
            return timedelta(hours=hours, minutes=minutes)
            
        raise forms.ValidationError('Formato de tiempo no válido')


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Evidencia
        fields = ['comentario', 'foto']

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['puntaje']
        widgets = {
            'puntaje': forms.RadioSelect(choices=[(i, '⭐' * i) for i in range(1, 6)])
        }  
class TiendaConfiguracionForm(forms.ModelForm):
    class Meta:
        model = TiendaConfiguracion
        fields = ['recordatorios_activos', 'metodo_recordatorios']
        widgets = {
            'metodo_recordatorios': forms.RadioSelect
        }# hola 