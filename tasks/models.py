from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

class Tienda(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class EmpleadoPerfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    es_jefe = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({'Jefe' if self.es_jefe else 'Empleado'})"


class Tarea(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    jefe = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas_creadas')
    empleados = models.ManyToManyField(EmpleadoPerfil, related_name='tareas_asignadas')
    tiempo_estimado = models.DurationField(help_text="Formato: HH:MM")
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    completada = models.BooleanField(default=False)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    aceptada_por = models.ManyToManyField(EmpleadoPerfil, blank=True, related_name="tareas_aceptadas")
    
    PRIORIDADES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='Media')

    def __str__(self):
        return self.titulo

    def tiempo_real_ejecucion(self):
        if self.completada and self.fecha_completada:
            aceptacion = AceptacionTarea.objects.filter(tarea=self).order_by('fecha_aceptacion').first()
            if aceptacion:
                duracion = self.fecha_completada - aceptacion.fecha_aceptacion
                # Convertir a horas y minutos
                total_seconds = int(duracion.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return timedelta(hours=hours, minutes=minutes)
            return timedelta(0)  # Si no hay aceptación, devuelve 0
        return None  # Si no está completada, devuelve None

class PlantillaTarea(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    jefe = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plantillas_creadas')
    tiempo_estimado = models.DurationField()
    PRIORIDADES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='Media')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plantilla: {self.titulo}"

    def crear_tarea(self):
        return Tarea(
            titulo=self.titulo,
            descripcion=self.descripcion,
            jefe=self.jefe,
            tiempo_estimado=self.tiempo_estimado,
            prioridad=self.prioridad
        )

class Evidencia(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    empleado = models.ForeignKey(EmpleadoPerfil, on_delete=models.CASCADE)
    comentario = models.TextField(blank=True)
    foto = models.ImageField(upload_to='evidencias/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia de {self.empleado.user.username} - {self.tarea.titulo}"


class Calificacion(models.Model):
    tarea = models.OneToOneField(Tarea, on_delete=models.CASCADE)
    puntaje = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField(blank=True)
    
    def __str__(self):
        return f"Calificación: {self.puntaje} - {self.tarea.titulo}"

# This model is for notifications related to tasks and employees.
class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Para {self.usuario.username} - {'Leída' if self.leida else 'No leída'}"

class AceptacionTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    empleado = models.ForeignKey(EmpleadoPerfil, on_delete=models.CASCADE)
    fecha_aceptacion = models.DateTimeField()

    def __str__(self):
        return f"{self.empleado.user.username} aceptó {self.tarea.titulo}"
    
class TiendaConfiguracion(models.Model):
     METODOS = [
        ('pantalla', 'Mostrar en pantalla'),
        ('correo', 'Enviar por correo'),
    ]
    
     tienda = models.OneToOneField(Tienda, on_delete=models.CASCADE, related_name='configuracion')
     recordatorios_activos = models.BooleanField(default=True)
     metodo_recordatorios = models.CharField(max_length=10, choices=METODOS, default='pantalla')

     def __str__(self):
        return f"Configuración de {self.tienda.nombre}"
