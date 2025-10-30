"""
Vistas para conversaciones de WhatsApp
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Conversacion, Lead
import json


@login_required
def whatsapp_detail(request, conversacion_id):
    """Detalle de una conversacion de WhatsApp"""
    conversacion = get_object_or_404(
        Conversacion.objects.select_related('lead', 'agente_humano'),
        id=conversacion_id
    )
    
    # Obtener todas las conversaciones del mismo lead para contexto
    conversaciones_lead = Conversacion.objects.filter(
        lead=conversacion.lead
    ).order_by('created_at')
    
    context = {
        'conversacion': conversacion,
        'lead': conversacion.lead,
        'conversaciones_lead': conversaciones_lead,
    }
    
    return render(request, 'callcenter/whatsapp_detail.html', context)


@login_required
@require_POST
def whatsapp_reply(request, conversacion_id):
    """Responder a una conversacion de WhatsApp"""
    try:
        conversacion = get_object_or_404(Conversacion, id=conversacion_id)
        data = json.loads(request.body)
        
        respuesta = data.get('respuesta', '').strip()
        if not respuesta:
            return JsonResponse({
                'success': False,
                'error': 'La respuesta no puede estar vacia'
            }, status=400)
        
        # Actualizar la conversacion
        conversacion.respuesta_sistema = respuesta
        conversacion.agente_humano = request.user
        conversacion.save()
        
        # Aqui se integraria con la API de WhatsApp para enviar el mensaje
        # Por ahora solo guardamos en la base de datos
        
        return JsonResponse({
            'success': True,
            'message': 'Respuesta enviada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
