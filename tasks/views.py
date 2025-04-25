# Django utils y decoradores
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from .models import AceptacionTarea
from django.utils.timezone import localtime

# Formularios
from .forms import (
    RegistroEmpleadoForm,
    RegistroJefeForm,
    CrearTareaForm,
    EvidenciaForm,
    CalificacionForm
)

# Modelos
from .models import EmpleadoPerfil, Tarea, Evidencia, Calificacion, Notificacion


@login_required
def LogoutView(request):
    logout(request)
    return redirect('index')

def index(request):
    return render(request, 'index.html')

def registro_empleado(request):
    if request.method == 'POST':
        form = RegistroEmpleadoForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('redireccion_dashboard')
    else:
        form = RegistroEmpleadoForm()
    return render(request, 'registro_empleado.html', {'form': form})

def registro_jefe(request):
    if request.method == 'POST':
        form = RegistroJefeForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('redireccion_dashboard')
    else:
        form = RegistroJefeForm()
    return render(request, 'registro_jefe.html', {'form': form})

@login_required
def redireccion_dashboard(request):
    try:
        perfil = EmpleadoPerfil.objects.get(user=request.user)
        return redirect('dashboard_jefe' if perfil.es_jefe else 'dashboard_empleado')
    except EmpleadoPerfil.DoesNotExist:
        return render(request, 'tasks/no_perfil.html')

@login_required
def dashboard_jefe(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha')
    jefe = EmpleadoPerfil.objects.get(user=request.user)
    tareas_qs = Tarea.objects.filter(jefe=request.user)
    tareas_recientes = tareas_qs.order_by('-fecha_asignacion')[:5]


    return render(request, 'dashboard_jefe.html', {
        'tareas_recientes': tareas_recientes,
        'tareas_pendientes': tareas_qs.filter(completada=False).count(),
        'tareas_completadas': tareas_qs.filter(completada=True).count(),
        'empleado_count': EmpleadoPerfil.objects.filter(tienda=jefe.tienda, es_jefe=False).count(),
        'notificaciones': notificaciones
    })

@login_required
def jefe_crear_tarea(request):
    jefe = EmpleadoPerfil.objects.get(user=request.user)
    empleados = EmpleadoPerfil.objects.filter(tienda=jefe.tienda, es_jefe=False)
    tareas = Tarea.objects.filter(jefe=request.user)

    if request.method == 'POST':
        form = CrearTareaForm(request.POST)
        form.fields['empleados'].queryset = empleados
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.jefe = request.user
            tarea.save()
            form.save_m2m()
             # ✅ Notificar a cada empleado asignado (dentro del if)
        for emp in form.cleaned_data['empleados']:
            Notificacion.objects.create(
                usuario=emp.user,
                mensaje=f"Tu jefe de tienda te ha asignado una nueva tarea: {tarea.titulo}"
            )

        return redirect('jefe_crear_tarea')
            
    else:
        form = CrearTareaForm()
        form.fields['empleados'].queryset = empleados

    return render(request, 'jefe_crear_tarea.html', {'form': form, 'tareas': tareas})

@login_required
def clean_empleados(self):
    empleados = self.cleaned_data.get('empleados')
    if not empleados:
        raise forms.ValidationError("Debes asignar al menos un empleado.")
    return empleados

@login_required
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, jefe=request.user)
    tarea.delete()
    return redirect('revisar_tareas')

@login_required
def detalle_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, jefe=request.user)
    evidencias = Evidencia.objects.filter(tarea=tarea)
    calificacion = Calificacion.objects.filter(tarea=tarea).first()

    form = None  # 👈 aseguramos que 'form' existe

    if request.method == 'POST' and tarea.completada and not calificacion:
        form = CalificacionForm(request.POST)
        if form.is_valid():
            cal = form.save(commit=False)
            cal.tarea = tarea
            cal.save()
             # Notificar a cada empleado asignado
            for empleado in tarea.empleados.all():
                Notificacion.objects.create(
                    usuario=empleado.user,
                    mensaje=f"Tu tarea '{tarea.titulo}' ha sido calificada con {cal.puntaje} estrellas")
            
            return redirect('detalle_tarea', tarea_id=tarea.id)
    elif tarea.completada and not calificacion:
        form = CalificacionForm()  # 👈 solo mostramos el formulario si se puede calificar

    return render(request, 'detalle_tarea.html', {
        'tarea': tarea,
        'evidencias': evidencias,
        'form': form,
        'calificacion': calificacion
    })

@login_required
def jefe_empleados(request):
    jefe = EmpleadoPerfil.objects.get(user=request.user)
    empleados = EmpleadoPerfil.objects.filter(tienda=jefe.tienda, es_jefe=False)

    data = []
    empleados_activos = 0
    tareas_pendientes = 0

    for emp in empleados:
        tareas_activas = emp.tareas_asignadas.filter(completada=False)
        tareas_hechas = emp.tareas_asignadas.filter(completada=True)

        if tareas_activas.exists():
            empleados_activos += 1
            tareas_pendientes += tareas_activas.count()

        data.append({
            'empleado': emp,
            'tiene_tarea': tareas_activas.exists(),
            'cantidad_tareas': tareas_activas.count(),
            'tareas_pendientes': tareas_activas,
            'tareas_completadas': tareas_hechas
        })

    return render(request, 'jefe_empleados.html', {
        'data': data,
        'empleados': empleados,
        'empleados_activos': empleados_activos,
        'tareas_pendientes': tareas_pendientes,
    })

@login_required
def dashboard_empleado(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha')
    perfil = EmpleadoPerfil.objects.get(user=request.user)
    tareas = Tarea.objects.filter(empleados=perfil)
    # Obtener calificaciones para mostrar
    tareas_con_calificacion = []
    for tarea in tareas:
        calificacion = Calificacion.objects.filter(tarea=tarea).first()
        tareas_con_calificacion.append({
            'tarea': tarea,
            'calificacion': calificacion
        })
    tareas_pendientes = tareas.filter(completada=False)
    tareas_completadas = tareas.filter(completada=True)

    if request.method == 'POST':
        tarea_id = request.POST.get('tarea_id')
        tarea = Tarea.objects.get(id=tarea_id)
        form = EvidenciaForm(request.POST, request.FILES)
        if form.is_valid():
            evidencia = form.save(commit=False)
            evidencia.empleado = perfil
            evidencia.tarea = tarea
            evidencia.save()

            tarea.completada = True
            tarea.fecha_completada = timezone.now()
            Notificacion.objects.create(
            usuario=tarea.jefe,
            mensaje=f"{request.user.username} ha completado la tarea: {tarea.titulo}")
            tarea.save()

            return redirect('dashboard_empleado')
    else:
        form = EvidenciaForm()

    return render(request, 'dashboard_empleado.html', {
        'tareas': tareas,
        'tareas_pendientes': tareas_pendientes,
        'tareas_completadas': tareas_completadas,
        'form': form,
        'notificaciones': notificaciones,
        'tareas_con_calificacion': tareas_con_calificacion
    })

@login_required
def aceptar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    empleado = EmpleadoPerfil.objects.get(user=request.user)

    if empleado in tarea.empleados.all() and empleado not in tarea.aceptada_por.all():
        tarea.aceptada_por.add(empleado)

        # 💾 Guardar la hora local de aceptación
        AceptacionTarea.objects.create(
            tarea=tarea,
            empleado=empleado,
            fecha_aceptacion=localtime()  # Hora local (Colombia si settings está bien)
        )

        Notificacion.objects.create(
            usuario=tarea.jefe,
            mensaje=f"{empleado.user.username} ha aceptado la tarea: {tarea.titulo}"
        )

    return redirect('dashboard_empleado')

@login_required
def marcar_notificaciones_leidas(request):
    Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
    return redirect('dashboard_empleado')  # O 'dashboard_jefe' si es para el jefe

@login_required
def marcar_notificaciones_leidas_Jefe(request):
    Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
    return redirect('dashboard_jefe')  # O 'dashboard_jefe' si es para el jefe

@login_required
def revisar_tareas(request):
    jefe = EmpleadoPerfil.objects.get(user=request.user)
    tareas = Tarea.objects.filter(jefe=request.user).order_by('-fecha_asignacion')

    return render(request, 'revisar_tareas.html', {
        'tareas': tareas,
    })
    
@login_required
def detalle_tarea_empleado(request, tarea_id):
    perfil = EmpleadoPerfil.objects.get(user=request.user)
    tarea = get_object_or_404(Tarea, id=tarea_id, empleados=perfil)
    
    # Validar que el empleado tiene acceso a esta tarea
    if perfil not in tarea.empleados.all():
        return redirect('dashboard_empleado')

    calificacion = Calificacion.objects.filter(tarea=tarea).first()
    evidencias = Evidencia.objects.filter(tarea=tarea, empleado=perfil)

    return render(request, 'detalle_tarea_empleado.html', {
        'tarea': tarea,
        'calificacion': calificacion,
        'evidencias': evidencias
    })
