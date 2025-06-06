from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Rutas públicas y de autenticación
urlpatterns = [
    path('', views.index, name='index'),  # Página de inicio
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # Login personalizado
    path('logout/', views.LogoutView, name='logout'),  # Logout
]

# Rutas de registro de usuarios
urlpatterns += [
    path('registro/empleado/', views.registro_empleado, name='registro_empleado'),  # Registro como empleado
    path('registro/jefe/', views.registro_jefe, name='registro_jefe'),  # Registro como jefe
]

# Ruta para redirección según tipo de usuario
urlpatterns += [
    path('dashboard/', views.redireccion_dashboard, name='redireccion_dashboard'),
]

# Vistas para empleados
urlpatterns += [
    path('empleado/', views.dashboard_empleado, name='dashboard_empleado'),  # Dashboard del empleado
    path('empleado/aceptar-tarea/<int:tarea_id>/', views.aceptar_tarea, name='aceptar_tarea'),
    path('notificaciones/leidas/', views.marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),
    path('tarea/<int:tarea_id>/detalle-empleado/', views.detalle_tarea_empleado, name='detalle_tarea_empleado')

]

# Vistas para jefes
urlpatterns += [
    path('jefe/', views.dashboard_jefe, name='dashboard_jefe'),  # Dashboard del jefe
    path('jefe/crear-tarea/', views.jefe_crear_tarea, name='jefe_crear_tarea'),  # Crear tarea
    path('jefe/empleados/', views.jefe_empleados, name='jefe_empleados'),  # Ver empleados
    path('notificaciones/leidasJefe/', views.marcar_notificaciones_leidas_Jefe, name='marcar_notificaciones_leidas_Jefe'),
    path('jefe/revisar-tareas/', views.revisar_tareas, name='revisar_tareas'),
    
    # Nuevas rutas para plantillas
    path('jefe/plantillas/', views.lista_plantillas, name='lista_plantillas'),
    path('jefe/plantillas/crear/', views.crear_plantilla, name='crear_plantilla'),
    path('jefe/plantillas/<int:plantilla_id>/editar/', views.editar_plantilla, name='editar_plantilla'),
    path('jefe/plantillas/<int:plantilla_id>/eliminar/', views.eliminar_plantilla, name='eliminar_plantilla'),
    path('jefe/plantillas/<int:plantilla_id>/usar/', views.usar_plantilla, name='usar_plantilla'),
]

# Gestión de tareas por el jefe
urlpatterns += [
    path('jefe/eliminar-tarea/<int:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea'),  # Eliminar tarea
    path('jefe/tarea/<int:tarea_id>/', views.detalle_tarea, name='detalle_tarea'),  # Detalles de tarea
    path('jefe/tarea/<int:tarea_id>/editar/', views.editar_tarea, name='editar_tarea'),  # Editar tarea
]