from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def format_duration(duration):
    """
    Formatea un objeto timedelta en formato 'HH:MM'
    """
    if not isinstance(duration, timedelta):
        return ''
    
    # Convertir a segundos totales
    total_seconds = int(duration.total_seconds())
    
    # Calcular horas y minutos
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    # Formatear como HH:MM
    return f"{hours:02d}:{minutes:02d}" 