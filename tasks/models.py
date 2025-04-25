from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

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
    tiempo_estimado = models.DurationField()
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
            # Aquí puedes hacer lógica para buscar la primera aceptación también
            return self.fecha_completada - self.fecha_asignacion
        return None
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
    puntaje = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=3)
    comentario = models.TextField(blank=True)
    
def __str__(self):
    return f"Calificación: {self.puntuacion} - {self.tarea.titulo}"
    
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
