"""
Views para el Call Center IA
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
import pytz

from .models import (
    Operador, Producto, Lead, Conversacion, LlamadaIA, Venta,
    ClasificacionLead, EstadoLead, TipoServicio
)
from .ai_services import CallAI
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET


@login_required
def dashboard(request):
    """Dashboard principal del Call Center"""
    
    # Estadísticas generales
    total_leads = Lead.objects.count()
    leads_hot = Lead.objects.filter(clasificacion=ClasificacionLead.HOT).count()
    leads_warm = Lead.objects.filter(clasificacion=ClasificacionLead.WARM).count()
    leads_cold = Lead.objects.filter(clasificacion=ClasificacionLead.COLD).count()
    
    total_ventas = Venta.objects.count()
    total_conversaciones = Conversacion.objects.count()
    
    # Ventas del mes
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ventas_mes = Venta.objects.filter(fecha_venta__gte=inicio_mes).count()
    ingresos_mes = Venta.objects.filter(fecha_venta__gte=inicio_mes).aggregate(
        total=Sum('precio_final')
    )['total'] or 0
    
    # Score promedio
    score_promedio = Lead.objects.aggregate(Avg('score'))['score__avg'] or 0
    
    # Leads recientes (últimos 10)
    leads_recientes = Lead.objects.select_related(
        'operador_interes', 'producto_interes', 'agente_asignado'
    ).order_by('-created_at')[:10]
    
    # Conversaciones recientes
    conversaciones_recientes = Conversacion.objects.select_related(
        'lead'
    ).order_by('-created_at')[:10]
    
    # Ventas recientes
    ventas_recientes = Venta.objects.select_related(
        'lead', 'producto', 'agente'
    ).order_by('-fecha_venta')[:10]
    
    # Distribución por operador
    leads_por_operador = Lead.objects.filter(
        operador_interes__isnull=False
    ).values('operador_interes__nombre').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Distribución por tipo de servicio
    leads_por_servicio = Lead.objects.filter(
        tipo_servicio_interes__isnull=False
    ).values('tipo_servicio_interes').annotate(
        total=Count('id')
    )
    
    # Top productos
    productos_populares = Producto.objects.annotate(
        num_leads=Count('leads')
    ).order_by('-num_leads')[:5]
    
    context = {
        'total_leads': total_leads,
        'leads_hot': leads_hot,
        'leads_warm': leads_warm,
        'leads_cold': leads_cold,
        'total_ventas': total_ventas,
        'total_conversaciones': total_conversaciones,
        'ventas_mes': ventas_mes,
        'ingresos_mes': ingresos_mes,
        'score_promedio': round(score_promedio, 1),
        'leads_recientes': leads_recientes,
        'conversaciones_recientes': conversaciones_recientes,
        'ventas_recientes': ventas_recientes,
        'leads_por_operador': leads_por_operador,
        'leads_por_servicio': leads_por_servicio,
        'productos_populares': productos_populares,
        'porcentaje_hot': round((leads_hot / total_leads * 100) if total_leads > 0 else 0, 1),
        'porcentaje_warm': round((leads_warm / total_leads * 100) if total_leads > 0 else 0, 1),
        'porcentaje_cold': round((leads_cold / total_leads * 100) if total_leads > 0 else 0, 1),
    }
    
    return render(request, 'callcenter/dashboard_modern.html', context)


@login_required
def whatsapp_dashboard(request):
    """Dashboard para agentes: conversaciones de WhatsApp y cola de mensajes."""
    # Conversaciones recientes y no asignadas
    # Nota: Conversacion tiene `created_at` pero no `updated_at` — usar created_at
    recientes = Conversacion.objects.select_related('lead').order_by('-created_at')[:50]
    sin_asignar = Conversacion.objects.filter(lead__agente_asignado__isnull=True).count()

    # Estadísticas rápidas
    total_conversaciones = Conversacion.objects.count()
    abiertas = Conversacion.objects.filter(estado='open').count() if hasattr(Conversacion, 'estado') else 0

    context = {
        'recientes': recientes,
        'sin_asignar': sin_asignar,
        'total_conversaciones': total_conversaciones,
        'abiertas': abiertas,
    }
    return render(request, 'callcenter/whatsapp_dashboard.html', context)


@login_required
def calls_dashboard(request):
    """Vista administrativa para monitorear llamadas IA y métricas globales."""
    if not request.user.is_superuser:
        # Solo administradores pueden ver métricas globales
        return redirect('callcenter:dashboard')

    llamadas_recientes = LlamadaIA.objects.select_related('lead').order_by('-created_at')[:50]
    llamadas_total = LlamadaIA.objects.count()
    llamadas_exitosas = LlamadaIA.objects.filter(resultado='success').count() if hasattr(LlamadaIA, 'resultado') else 0

    context = {
        'llamadas_recientes': llamadas_recientes,
        'llamadas_total': llamadas_total,
        'llamadas_exitosas': llamadas_exitosas,
    }
    return render(request, 'callcenter/calls_dashboard.html', context)


@login_required
def leads_list(request):
    """Lista de leads con filtros"""
    
    # Obtener filtros
    clasificacion = request.GET.get('clasificacion', '')
    estado = request.GET.get('estado', '')
    operador = request.GET.get('operador', '')
    busqueda = request.GET.get('q', '')
    
    # Query base
    leads = Lead.objects.select_related(
        'operador_interes', 'producto_interes', 'agente_asignado'
    ).all()
    
    # Aplicar filtros
    if clasificacion:
        leads = leads.filter(clasificacion=clasificacion)
    
    if estado:
        leads = leads.filter(estado=estado)
    
    if operador:
        leads = leads.filter(operador_interes__id=operador)
    
    if busqueda:
        leads = leads.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido__icontains=busqueda) |
            Q(telefono__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(zona__icontains=busqueda)
        )
    
    # Ordenar
    leads = leads.order_by('-score', '-created_at')
    
    # Obtener operadores para el filtro
    operadores = Operador.objects.all()
    
    context = {
        'leads': leads,
        'operadores': operadores,
        'clasificacion_actual': clasificacion,
        'estado_actual': estado,
        'operador_actual': operador,
        'busqueda': busqueda,
    }
    
    return render(request, 'callcenter/leads_list.html', context)


@login_required
def lead_detail(request, lead_id):
    """Detalle de un lead"""
    
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Conversaciones del lead
    conversaciones = lead.conversaciones.order_by('-created_at')
    
    # Llamadas del lead
    llamadas = lead.llamadas.order_by('-created_at')
    
    # Productos sugeridos
    if lead.tipo_servicio_interes:
        productos_sugeridos = Producto.objects.filter(
            tipo=lead.tipo_servicio_interes,
            is_active=True
        ).order_by('-is_destacado', 'precio_mensual')[:5]
    else:
        productos_sugeridos = Producto.objects.filter(
            is_active=True,
            is_destacado=True
        )[:5]
    
    # Todos los operadores para el modal de edicion
    operadores = Operador.objects.filter(is_active=True).order_by('nombre')
    
    # Todos los productos para el modal de edicion
    todos_productos = Producto.objects.filter(is_active=True).order_by('operador__nombre', 'nombre_plan')
    
    context = {
        'lead': lead,
        'conversaciones': conversaciones,
        'llamadas': llamadas,
        'productos_sugeridos': productos_sugeridos,
        'operadores': operadores,
        'todos_productos': todos_productos,
    }
    
    return render(request, 'callcenter/lead_detail.html', context)


@login_required
def productos_list(request):
    """Lista de productos"""
    
    # Filtros
    operador = request.GET.get('operador', '')
    tipo = request.GET.get('tipo', '')
    destacados = request.GET.get('destacados', '')
    
    # Query base
    productos = Producto.objects.select_related('operador').filter(is_active=True)
    
    # Aplicar filtros
    if operador:
        productos = productos.filter(operador__id=operador)
    
    if tipo:
        productos = productos.filter(tipo=tipo)
    
    if destacados:
        productos = productos.filter(is_destacado=True)
    
    # Ordenar
    productos = productos.order_by('operador__orden', '-is_destacado', 'precio_mensual')
    
    # Operadores para filtro
    operadores = Operador.objects.all().order_by('orden')
    
    context = {
        'productos': productos,
        'operadores': operadores,
        'operador_actual': operador,
        'tipo_actual': tipo,
        'destacados_actual': destacados,
    }
    
    return render(request, 'callcenter/productos_list.html', context)


@login_required
def api_lead_stats(request):
    """API para estadísticas de leads (para gráficos)"""
    
    # Leads por día (últimos 30 días)
    hoy = timezone.now()
    hace_30_dias = hoy - timedelta(days=30)
    
    leads_por_dia = []
    for i in range(30):
        dia = hace_30_dias + timedelta(days=i)
        dia_siguiente = dia + timedelta(days=1)
        
        count = Lead.objects.filter(
            created_at__gte=dia,
            created_at__lt=dia_siguiente
        ).count()
        
        leads_por_dia.append({
            'fecha': dia.strftime('%Y-%m-%d'),
            'total': count
        })
    
    # Distribución por clasificación
    distribucion = {
        'hot': Lead.objects.filter(clasificacion=ClasificacionLead.HOT).count(),
        'warm': Lead.objects.filter(clasificacion=ClasificacionLead.WARM).count(),
        'cold': Lead.objects.filter(clasificacion=ClasificacionLead.COLD).count(),
    }
    
    return JsonResponse({
        'leads_por_dia': leads_por_dia,
        'distribucion': distribucion,
    })


@login_required
def api_ventas_stats(request):
    """API para estadísticas de ventas"""
    
    # Ventas por mes (últimos 6 meses)
    hoy = timezone.now()
    
    ventas_por_mes = []
    for i in range(6):
        mes = hoy - timedelta(days=30*i)
        inicio_mes = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if i > 0:
            fin_mes = (hoy - timedelta(days=30*(i-1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            fin_mes = hoy
        
        ventas = Venta.objects.filter(
            fecha_venta__gte=inicio_mes,
            fecha_venta__lt=fin_mes
        )
        
        total = ventas.count()
        ingresos = ventas.aggregate(Sum('precio_final'))['precio_final__sum'] or 0
        
        ventas_por_mes.insert(0, {
            'mes': inicio_mes.strftime('%B %Y'),
            'total': total,
            'ingresos': float(ingresos)
        })
    
    return JsonResponse({
        'ventas_por_mes': ventas_por_mes
    })


@login_required
@require_POST
def api_generate_script(request):
    """Genera un script de llamada para un lead usando CallAI.generar_script_llamada

    Espera parámetros POST: lead_id (int), tipo_llamada (opcional, 'SALIENTE'|'ENTRANTE')
    """
    try:
        # soportar JSON body o form-encoded
        data = request.POST.dict()
        if not data:
            import json
            try:
                data = json.loads(request.body.decode('utf-8') or '{}')
            except Exception:
                data = {}

        lead_id = data.get('lead_id')
        tipo = data.get('tipo_llamada', 'SALIENTE')

        if not lead_id:
            return JsonResponse({'success': False, 'error': 'lead_id es requerido'}, status=400)

        lead = Lead.objects.get(id=int(lead_id))
        script = CallAI.generar_script_llamada(lead, tipo)

        return JsonResponse({'success': True, 'script': script})

    except Lead.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lead no encontrado'}, status=404)
    except Exception as e:
        import logging
        logging.exception('Error generando script')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_GET
def api_recent_conversations(request):
    """Devuelve las conversaciones recientes en JSON (para polling en el dashboard de agentes)."""
    try:
        limit = int(request.GET.get('limit', 20))
    except Exception:
        limit = 20

    convers = Conversacion.objects.select_related('lead', 'agente_humano').order_by('-created_at')[:limit]
    data = []
    for c in convers:
        data.append({
            'id': c.id,
            'lead_id': c.lead.id,
            'lead_nombre': c.lead.nombre_completo,
            'mensaje_cliente': (c.mensaje_cliente[:200] + '...') if c.mensaje_cliente and len(c.mensaje_cliente) > 200 else (c.mensaje_cliente or ''),
            'respuesta_sistema': c.respuesta_sistema or '',
            'created_at': c.created_at.isoformat(),
            'agente_id': c.agente_humano.id if c.agente_humano else None,
            'agente_nombre': c.agente_humano.get_full_name() if c.agente_humano else None,
        })

    return JsonResponse({'success': True, 'conversaciones': data})


@login_required
@require_POST
def api_assign_conversation(request):
    """Asignar una conversación al usuario actual (POST: conv_id)."""
    try:
        data = request.POST.dict() or {}
        if not data:
            import json
            try:
                data = json.loads(request.body.decode('utf-8') or '{}')
            except Exception:
                data = {}

        conv_id = data.get('conv_id') or data.get('id')
        if not conv_id:
            return JsonResponse({'success': False, 'error': 'conv_id es requerido'}, status=400)

        conv = Conversacion.objects.select_related('lead').get(id=int(conv_id))
        conv.agente_humano = request.user
        conv.save()

        # opcional: asignar el lead al agente
        lead = conv.lead
        if not lead.agente_asignado:
            lead.agente_asignado = request.user
            lead.save(update_fields=['agente_asignado'])

        return JsonResponse({'success': True, 'conv_id': conv.id, 'assigned_to': request.user.get_full_name() or request.user.username})

    except Conversacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversación no encontrada'}, status=404)
    except Exception as e:
        import logging
        logging.exception('Error asignando conversación')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
