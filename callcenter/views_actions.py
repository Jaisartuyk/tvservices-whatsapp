"""
Vistas para acciones de WhatsApp, Llamadas y Email
"""
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Lead, Conversacion, LlamadaIA
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)


@login_required
@require_POST
def api_send_whatsapp(request, lead_id):
    """
    Enviar mensaje de WhatsApp a un lead
    POST: { "mensaje": "texto del mensaje" }
    """
    try:
        lead = get_object_or_404(Lead, id=lead_id)
        
        # Obtener mensaje del body
        data = json.loads(request.body.decode('utf-8'))
        mensaje = data.get('mensaje', '')
        
        if not mensaje:
            return JsonResponse({
                'success': False,
                'error': 'El mensaje es requerido'
            }, status=400)
        
        # Crear conversación
        conversacion = Conversacion.objects.create(
            lead=lead,
            canal='WHATSAPP',
            mensaje=mensaje,
            agente_humano=request.user,
            created_at=timezone.now()
        )
        
        # TODO: Integrar con WhatsApp Business API
        # Por ahora solo registramos la conversación
        
        return JsonResponse({
            'success': True,
            'message': 'Mensaje enviado correctamente',
            'conversacion_id': conversacion.id,
            'lead_nombre': lead.nombre_completo,
            'telefono': lead.telefono
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Lead no encontrado'
        }, status=404)
    except Exception as e:
        logger.exception('Error enviando WhatsApp')
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_POST
def api_whatsapp_webhook(request):
    """
    Webhook para recibir mensajes de WhatsApp
    Este endpoint será llamado por WhatsApp Business API
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        # Extraer información del webhook
        # La estructura depende de la API de WhatsApp que uses
        telefono = data.get('from', '')
        mensaje = data.get('text', {}).get('body', '')
        
        if not telefono or not mensaje:
            return JsonResponse({
                'success': False,
                'error': 'Datos incompletos'
            }, status=400)
        
        # Buscar lead por teléfono
        try:
            lead = Lead.objects.get(telefono=telefono)
        except Lead.DoesNotExist:
            # Crear nuevo lead si no existe
            lead = Lead.objects.create(
                telefono=telefono,
                nombre='Cliente',
                apellido='WhatsApp',
                zona='No especificada',
                estado='NUEVO',
                clasificacion='COLD',
                score=30
            )
        
        # Crear conversación
        conversacion = Conversacion.objects.create(
            lead=lead,
            canal='WHATSAPP',
            mensaje=mensaje,
            created_at=timezone.now()
        )
        
        # TODO: Procesar con IA y generar respuesta automática
        
        return JsonResponse({
            'success': True,
            'conversacion_id': conversacion.id
        })
        
    except Exception as e:
        logger.exception('Error en webhook de WhatsApp')
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def api_make_call(request, lead_id):
    """
    Iniciar llamada telefónica a un lead
    POST: { "tipo": "SALIENTE" }
    """
    try:
        lead = get_object_or_404(Lead, id=lead_id)
        
        # Obtener tipo de llamada
        data = json.loads(request.body.decode('utf-8'))
        tipo = data.get('tipo', 'SALIENTE')
        
        # Crear registro de llamada
        llamada = LlamadaIA.objects.create(
            lead=lead,
            tipo=tipo,
            agente_humano=request.user,
            created_at=timezone.now()
        )
        
        # TODO: Integrar con Twilio para hacer la llamada real
        # Por ahora solo registramos la intención
        
        return JsonResponse({
            'success': True,
            'message': 'Llamada iniciada',
            'llamada_id': llamada.id,
            'lead_nombre': lead.nombre_completo,
            'telefono': lead.telefono
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Lead no encontrado'
        }, status=404)
    except Exception as e:
        logger.exception('Error iniciando llamada')
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_POST
def api_call_webhook(request):
    """
    Webhook para recibir eventos de llamadas de Twilio
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        # Extraer información del webhook de Twilio
        call_sid = data.get('CallSid', '')
        call_status = data.get('CallStatus', '')
        duration = data.get('CallDuration', 0)
        
        # TODO: Actualizar registro de llamada con los datos
        
        return JsonResponse({
            'success': True,
            'call_sid': call_sid
        })
        
    except Exception as e:
        logger.exception('Error en webhook de llamadas')
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def api_send_email(request, lead_id):
    """
    Enviar email a un lead
    POST: { "asunto": "...", "mensaje": "..." }
    """
    try:
        lead = get_object_or_404(Lead, id=lead_id)
        
        if not lead.email:
            return JsonResponse({
                'success': False,
                'error': 'El lead no tiene email registrado'
            }, status=400)
        
        # Obtener datos del email
        data = json.loads(request.body.decode('utf-8'))
        asunto = data.get('asunto', '')
        mensaje = data.get('mensaje', '')
        
        if not asunto or not mensaje:
            return JsonResponse({
                'success': False,
                'error': 'Asunto y mensaje son requeridos'
            }, status=400)
        
        # TODO: Enviar email real usando Django Email o SendGrid
        # Por ahora solo registramos la conversación
        
        conversacion = Conversacion.objects.create(
            lead=lead,
            canal='EMAIL',
            mensaje=f"Asunto: {asunto}\n\n{mensaje}",
            agente_humano=request.user,
            created_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Email enviado correctamente',
            'conversacion_id': conversacion.id,
            'lead_nombre': lead.nombre_completo,
            'email': lead.email
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Lead no encontrado'
        }, status=404)
    except Exception as e:
        logger.exception('Error enviando email')
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
