"""
Vistas para dashboards específicos de WhatsApp y Llamadas
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Conversacion, LlamadaIA, Lead


@login_required
def whatsapp_dashboard(request):
    """
    Dashboard específico para gestión de conversaciones de WhatsApp
    """
    # Estadísticas generales
    total_conversaciones = Conversacion.objects.filter(canal='WHATSAPP').count()
    sin_asignar = Conversacion.objects.filter(
        canal='WHATSAPP',
        agente_humano__isnull=True
    ).count()
    abiertas = Conversacion.objects.filter(
        canal='WHATSAPP',
        agente_humano__isnull=False
    ).count()
    
    # Conversaciones recientes (últimas 50)
    conversaciones = Conversacion.objects.filter(
        canal='WHATSAPP'
    ).select_related(
        'lead',
        'agente_humano'
    ).order_by('-created_at')[:50]
    
    # Conversaciones por agente
    conversaciones_por_agente = Conversacion.objects.filter(
        canal='WHATSAPP',
        agente_humano__isnull=False
    ).values(
        'agente_humano__username',
        'agente_humano__first_name',
        'agente_humano__last_name'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    # Conversaciones de hoy
    hoy = timezone.now().date()
    conversaciones_hoy = Conversacion.objects.filter(
        canal='WHATSAPP',
        created_at__date=hoy
    ).count()
    
    context = {
        'total_conversaciones': total_conversaciones,
        'sin_asignar': sin_asignar,
        'abiertas': abiertas,
        'conversaciones_hoy': conversaciones_hoy,
        'conversaciones': conversaciones,
        'conversaciones_por_agente': conversaciones_por_agente,
    }
    
    return render(request, 'callcenter/whatsapp_dashboard.html', context)


@login_required
def calls_dashboard(request):
    """
    Dashboard específico para gestión de llamadas
    """
    # Estadísticas generales
    total_llamadas = LlamadaIA.objects.count()
    llamadas_hoy = LlamadaIA.objects.filter(
        created_at__date=timezone.now().date()
    ).count()
    
    # Llamadas por tipo
    llamadas_entrantes = LlamadaIA.objects.filter(tipo='ENTRANTE').count()
    llamadas_salientes = LlamadaIA.objects.filter(tipo='SALIENTE').count()
    
    # Llamadas por resultado
    llamadas_exitosas = LlamadaIA.objects.filter(
        resultado='EXITOSA'
    ).count()
    llamadas_no_contesto = LlamadaIA.objects.filter(
        resultado='NO_CONTESTO'
    ).count()
    llamadas_ocupado = LlamadaIA.objects.filter(
        resultado='OCUPADO'
    ).count()
    
    # Llamadas recientes (últimas 50)
    llamadas = LlamadaIA.objects.select_related(
        'lead',
        'agente_humano'
    ).order_by('-created_at')[:50]
    
    # Llamadas por agente
    llamadas_por_agente = LlamadaIA.objects.filter(
        agente_humano__isnull=False
    ).values(
        'agente_humano__username',
        'agente_humano__first_name',
        'agente_humano__last_name'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    # Duración promedio (solo llamadas con duración)
    from django.db.models import Avg
    duracion_promedio = LlamadaIA.objects.filter(
        duracion__isnull=False,
        duracion__gt=0
    ).aggregate(
        promedio=Avg('duracion')
    )['promedio'] or 0
    
    # Llamadas por día (últimos 7 días)
    hace_7_dias = timezone.now() - timedelta(days=7)
    llamadas_por_dia = []
    for i in range(7):
        dia = hace_7_dias + timedelta(days=i)
        dia_siguiente = dia + timedelta(days=1)
        count = LlamadaIA.objects.filter(
            created_at__gte=dia,
            created_at__lt=dia_siguiente
        ).count()
        llamadas_por_dia.append({
            'fecha': dia.strftime('%d/%m'),
            'total': count
        })
    
    context = {
        'total_llamadas': total_llamadas,
        'llamadas_hoy': llamadas_hoy,
        'llamadas_entrantes': llamadas_entrantes,
        'llamadas_salientes': llamadas_salientes,
        'llamadas_exitosas': llamadas_exitosas,
        'llamadas_no_contesto': llamadas_no_contesto,
        'llamadas_ocupado': llamadas_ocupado,
        'llamadas': llamadas,
        'llamadas_por_agente': llamadas_por_agente,
        'duracion_promedio': round(duracion_promedio, 2),
        'llamadas_por_dia': llamadas_por_dia,
    }
    
    return render(request, 'callcenter/calls_dashboard.html', context)
