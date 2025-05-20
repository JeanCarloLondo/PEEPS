# Django utils y decoradores
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from .models import AceptacionTarea
from django.utils.timezone import localtime
from datetime import timedelta, datetime

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
def jefe_empleados(request): # MODIFIED FUNCTION
    jefe = EmpleadoPerfil.objects.get(user=request.user, es_jefe=True)
    
    # --- Filtering ---
    selected_employee_id_str = request.GET.get('empleado_id')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Base queryset for employees to display in the detailed list
    empleados_qs_for_list = EmpleadoPerfil.objects.filter(tienda=jefe.tienda, es_jefe=False)
    
    selected_employee_id_int = None
    if selected_employee_id_str:
        try:
            selected_employee_id_int = int(selected_employee_id_str)
            empleados_qs_for_list = empleados_qs_for_list.filter(id=selected_employee_id_int)
        except ValueError:
            pass # Invalid employee_id, show all for list

    # --- Stats for the top cards (Store-wide) ---
    all_jefe_employees_storewide = EmpleadoPerfil.objects.filter(tienda=jefe.tienda, es_jefe=False)
    total_empleados_count_card = all_jefe_employees_storewide.count()
    
    empleados_activos_count_card = 0
    tareas_pendientes_total_count_card = 0
    active_employee_ids = set()

    for emp_stat in all_jefe_employees_storewide:
        if emp_stat.tareas_asignadas.filter(completada=False).exists():
            active_employee_ids.add(emp_stat.id)
        tareas_pendientes_total_count_card += emp_stat.tareas_asignadas.filter(completada=False).count()
    empleados_activos_count_card = len(active_employee_ids)
    # --- End Stats for top cards ---

    data_list = [] # Renamed from 'data' to avoid confusion with individual item 'data_item' in template
    for emp_perfil in empleados_qs_for_list:
        tareas_asignadas_historico = emp_perfil.tareas_asignadas.all()
        num_tareas_asignadas_historico = tareas_asignadas_historico.count()

        tareas_pendientes_empleado = tareas_asignadas_historico.filter(completada=False).order_by('-fecha_asignacion')
        
        tareas_completadas_base = tareas_asignadas_historico.filter(completada=True)
        
        tareas_completadas_periodo = tareas_completadas_base
        if fecha_inicio_str:
            try:
                fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio_str, '%Y-%m-%d'))
                tareas_completadas_periodo = tareas_completadas_periodo.filter(fecha_completada__gte=fecha_inicio_dt)
            except ValueError: pass
        if fecha_fin_str:
            try:
                fecha_fin_dt = timezone.make_aware(datetime.combine(datetime.strptime(fecha_fin_str, '%Y-%m-%d'), datetime.max.time()))
                tareas_completadas_periodo = tareas_completadas_periodo.filter(fecha_completada__lte=fecha_fin_dt)
            except ValueError: pass

        num_tareas_completadas_periodo = tareas_completadas_periodo.count()

        detailed_completed_tasks_list = []
        current_total_score_for_ranking = 0
        current_sum_of_ratings_periodo = 0
        current_count_of_rated_tasks_periodo = 0

        for tarea_item in tareas_completadas_periodo.select_related('jefe').prefetch_related('evidencia_set', 'calificacion'):
            tiempo_real = tarea_item.tiempo_real_ejecucion()
            tiempo_estimado = tarea_item.tiempo_estimado
            
            evidencias_tarea_empleado_list = Evidencia.objects.filter(tarea=tarea_item, empleado=emp_perfil)
            
            calificacion_tarea_item = None
            try:
                calificacion_tarea_item = tarea_item.calificacion
            except Calificacion.DoesNotExist:
                pass

            rating_points_task = 0
            if calificacion_tarea_item:
                rating_points_task = calificacion_tarea_item.puntaje
                current_sum_of_ratings_periodo += rating_points_task
                current_count_of_rated_tasks_periodo += 1

            timeliness_points_task = 0
            if tiempo_estimado and tiempo_estimado.total_seconds() > 0:
                if tiempo_real and tiempo_real.total_seconds() > 0:
                    if tiempo_real <= tiempo_estimado:
                        timeliness_points_task = 2
                    elif tiempo_real.total_seconds() <= tiempo_estimado.total_seconds() * 1.5:
                        timeliness_points_task = 1
                elif not tiempo_real or tiempo_real.total_seconds() == 0: # Completed instantly or not accepted
                     timeliness_points_task = 2
            
            current_total_score_for_ranking += rating_points_task + timeliness_points_task

            detailed_completed_tasks_list.append({
                'id': tarea_item.id,
                'titulo': tarea_item.titulo,
                'tiempo_estimado': tiempo_estimado,
                'tiempo_real_ejecucion': tiempo_real,
                'fecha_completada': tarea_item.fecha_completada,
                'evidencias': evidencias_tarea_empleado_list,
                'calificacion': calificacion_tarea_item,
                'rating_points': rating_points_task,
                'timeliness_points': timeliness_points_task,
                'task_score': rating_points_task + timeliness_points_task,
            })
        
        avg_rating_periodo_empleado = (current_sum_of_ratings_periodo / current_count_of_rated_tasks_periodo) if current_count_of_rated_tasks_periodo > 0 else 0

        data_list.append({
            'empleado': emp_perfil,
            'tiene_tarea_pendiente': tareas_pendientes_empleado.exists(),
            'cantidad_tareas_pendientes': tareas_pendientes_empleado.count(),
            'tareas_pendientes_list': tareas_pendientes_empleado,
            
            'num_tareas_asignadas_historico': num_tareas_asignadas_historico,
            'num_tareas_completadas_periodo': num_tareas_completadas_periodo,
            'detailed_completed_tasks_list': detailed_completed_tasks_list,
            'avg_rating_periodo': avg_rating_periodo_empleado,
            'num_tareas_calificadas_periodo': current_count_of_rated_tasks_periodo,
            'performance_score': current_total_score_for_ranking,
        })

    data_list.sort(key=lambda x: x['performance_score'], reverse=True)

    context = {
        'data_list': data_list,
        'empleados_count_for_card': total_empleados_count_card,
        'empleados_activos_for_card': empleados_activos_count_card,
        'tareas_pendientes_total_for_card': tareas_pendientes_total_count_card,
        
        'all_employees_for_filter': all_jefe_employees_storewide, # For the filter dropdown
        'selected_employee_id': selected_employee_id_int,
        'fecha_inicio_str': fecha_inicio_str,
        'fecha_fin_str': fecha_fin_str,
        'notificaciones': Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha'),
    }
    return render(request, 'jefe_empleados.html', context)

@login_required
def dashboard_empleado(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha')
    perfil = EmpleadoPerfil.objects.get(user=request.user)
    fecha_filtro = request.GET.get('filtro', 'todas')
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

 # Base query para tareas completadas
    tareas_completadas = Tarea.objects.filter(
        empleados=perfil, 
        completada=True
    ).prefetch_related('calificacion').order_by('-fecha_completada')
    
    # Aplicar filtros de fecha
    if fecha_filtro == 'semana':
        start_date = timezone.now() - timedelta(days=7)
        tareas_completadas = tareas_completadas.filter(fecha_completada__gte=start_date)
    elif fecha_filtro == 'mes':
        start_date = timezone.now() - timedelta(days=30)
        tareas_completadas = tareas_completadas.filter(fecha_completada__gte=start_date)
        
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
        'fecha_filtro': fecha_filtro,
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