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
from .ai_services import WhatsAppBotIA, LeadScorer


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
    ).order_by('-fecha_creacion')[:10]
    
    # Conversaciones recientes
    conversaciones_recientes = Conversacion.objects.select_related(
        'lead'
    ).order_by('-fecha')[:10]
    
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
        num_leads=Count('lead_producto_interes')
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
    
    return render(request, 'callcenter/dashboard.html', context)


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
    leads = leads.order_by('-score', '-fecha_creacion')
    
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
    conversaciones = lead.conversaciones.order_by('-fecha')
    
    # Llamadas del lead
    llamadas = lead.llamadas.order_by('-fecha_hora')
    
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
    
    context = {
        'lead': lead,
        'conversaciones': conversaciones,
        'llamadas': llamadas,
        'productos_sugeridos': productos_sugeridos,
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
            fecha_creacion__gte=dia,
            fecha_creacion__lt=dia_siguiente
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
