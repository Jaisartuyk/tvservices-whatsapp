import requests
import logging
from django.conf import settings
from typing import Optional, Dict, Any
from datetime import date, timedelta

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Servicio para enviar notificaciones por WhatsApp usando WaSender API"""
    
    def __init__(self):
        self.api_url = getattr(settings, 'WASENDER_API_URL', 'https://wasenderapi.com')
        self.api_key = getattr(settings, 'WASENDER_API_KEY', '')
        self.session_id = getattr(settings, 'WASENDER_SESSION_ID', '')
        self.webhook_url = getattr(settings, 'WASENDER_WEBHOOK_URL', '')
        self.webhook_secret = getattr(settings, 'WASENDER_WEBHOOK_SECRET', '')
        
    def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje de WhatsApp a un número específico
        
        Args:
            phone_number: Número de teléfono (con código de país, sin +)
            message: Mensaje a enviar
            
        Returns:
            Dict con la respuesta de la API
        """
        if not self.api_key:
            logger.error("WaSender API key no configurado")
            return {'success': False, 'error': 'API key no configurada'}
        
        # Limpiar el número de teléfono y agregar + si no lo tiene
        clean_phone = self._clean_phone_number(phone_number)
        if not clean_phone:
            logger.error(f"Número de teléfono inválido: {phone_number}")
            return {'success': False, 'error': 'Número de teléfono inválido'}
        
        # Asegurar que el número tenga el formato +57XXXXXXXXX
        if not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        url = f"{self.api_url}/api/send-message"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        payload = {
            'to': clean_phone,
            'message': message
        }
        
        # Agregar session_id si está configurado
        if self.session_id:
            payload['session_id'] = int(self.session_id)
        
        try:
            logger.info(f"Enviando WhatsApp a {clean_phone}")
            logger.info(f"URL: {url}")
            logger.info(f"Payload: {payload}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Mensaje enviado exitosamente a {clean_phone}")
            return {'success': True, 'data': result}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar mensaje a {clean_phone}: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error inesperado al enviar mensaje: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _clean_phone_number(self, phone: str) -> Optional[str]:
        """
        Limpia y valida el número de teléfono
        Soporta números de Colombia (+57) y Ecuador (+593)
        
        Args:
            phone: Número de teléfono a limpiar
            
        Returns:
            Número limpio o None si es inválido
        """
        if not phone:
            return None
        
        # Remover espacios, guiones, paréntesis, + etc.
        clean = ''.join(filter(str.isdigit, phone))
        
        # Manejar diferentes formatos según el país
        
        # Ecuador: números móviles empiezan con 09 (ej: 0968196046)
        if len(clean) == 10 and clean.startswith('09'):
            # Remover el 0 inicial y agregar código de Ecuador
            clean = '593' + clean[1:]  # 0968196046 -> 593968196046
        
        # Colombia: números móviles empiezan con 3 o 6
        elif len(clean) == 10 and clean.startswith(('3', '6')):
            clean = '57' + clean  # 3001234567 -> 573001234567
        
        # Número fijo colombiano sin código de área
        elif len(clean) == 7:
            clean = '571' + clean  # Asumir Bogotá
        
        # Si ya tiene código de país, validar que sea correcto
        elif len(clean) >= 11:
            if clean.startswith('593') and len(clean) == 12:  # Ecuador
                pass  # Ya está correcto
            elif clean.startswith('57') and len(clean) == 12:  # Colombia
                pass  # Ya está correcto
            else:
                # Otros países o formatos no soportados
                logger.warning(f"Formato de número no reconocido: {phone}")
        
        # Validar longitud final
        if len(clean) < 10:
            return None
            
        return clean


class NotificationService:
    """Servicio para manejar notificaciones de vencimiento de suscripciones"""
    
    def __init__(self):
        self.whatsapp = WhatsAppService()
    
    def send_expiration_notification(self, subscription, days_until_expiration: int) -> Dict[str, Any]:
        """
        Envía notificación de vencimiento de suscripción
        
        Args:
            subscription: Objeto Subscription
            days_until_expiration: Días hasta el vencimiento
            
        Returns:
            Dict con el resultado del envío
        """
        from .models import NotificationLog
        
        if not subscription.cliente.telefono:
            return {'success': False, 'error': 'Cliente no tiene teléfono registrado'}
        
        message = self._create_expiration_message(subscription, days_until_expiration)
        
        # Crear registro de notificación
        notification_log = NotificationLog.objects.create(
            subscription=subscription,
            notification_type=NotificationLog.NotificationType.EXPIRATION_WARNING,
            phone_number=subscription.cliente.telefono,
            message_content=message,
            days_notice=days_until_expiration,
            status=NotificationLog.NotificationStatus.PENDING
        )
        
        # Enviar mensaje
        result = self.whatsapp.send_message(
            subscription.cliente.telefono,
            message
        )
        
        # Actualizar el registro según el resultado
        if result['success']:
            notification_log.mark_as_sent(result.get('data'))
            logger.info(f"Notificación enviada a {subscription.cliente.nombre_completo} - Suscripción {subscription.id}")
        else:
            notification_log.mark_as_failed(result.get('error'))
            logger.error(f"Error enviando notificación a {subscription.cliente.nombre_completo}: {result.get('error')}")
        
        return result
    
    def _create_expiration_message(self, subscription, days_until_expiration: int) -> str:
        """
        Crea el mensaje de notificación personalizado
        
        Args:
            subscription: Objeto Subscription
            days_until_expiration: Días hasta el vencimiento
            
        Returns:
            Mensaje formateado
        """
        cliente_name = subscription.cliente.nombre_completo
        service_name = subscription.service.nombre_mostrar
        expiration_date = subscription.end_date.strftime('%d/%m/%Y')
        price = subscription.price
        
        if days_until_expiration == 1:
            urgency = "¡MAÑANA!"
            emoji = "⚠️"
        elif days_until_expiration == 0:
            urgency = "¡HOY!"
            emoji = "🚨"
        else:
            urgency = f"en {days_until_expiration} días"
            emoji = "📅"
        
        message = f"""
{emoji} *TV Services - Recordatorio de Vencimiento*

Hola *{cliente_name}*,

Te recordamos que tu suscripción a *{service_name}* vence {urgency}.

📋 *Detalles:*
• Servicio: {service_name}
• Fecha de vencimiento: {expiration_date}
• Valor de renovación: ${price:,.0f}

💡 *Para renovar tu suscripción:*
1. Contacta con nosotros
2. Realiza el pago correspondiente
3. ¡Sigue disfrutando sin interrupciones!

📞 ¿Necesitas ayuda? Responde a este mensaje.

*TV Services* - Tu entretenimiento sin límites
        """.strip()
        
        return message
    
    def send_renewal_confirmation(self, subscription) -> Dict[str, Any]:
        """
        Envía confirmación de renovación de suscripción
        
        Args:
            subscription: Objeto Subscription renovado
            
        Returns:
            Dict con el resultado del envío
        """
        if not subscription.cliente.telefono:
            return {'success': False, 'error': 'Cliente no tiene teléfono registrado'}
        
        message = self._create_renewal_message(subscription)
        
        return self.whatsapp.send_message(
            subscription.cliente.telefono,
            message
        )
    
    def _create_renewal_message(self, subscription) -> str:
        """Crea mensaje de confirmación de renovación"""
        cliente_name = subscription.cliente.nombre_completo
        service_name = subscription.service.nombre_mostrar
        new_expiration = subscription.end_date.strftime('%d/%m/%Y')
        
        message = f"""
✅ *TV Services - Renovación Confirmada*

¡Hola *{cliente_name}*!

Tu suscripción a *{service_name}* ha sido renovada exitosamente.

📋 *Nueva información:*
• Servicio: {service_name}
• Nueva fecha de vencimiento: {new_expiration}
• Estado: Activa ✅

¡Gracias por confiar en nosotros! Sigue disfrutando de tu entretenimiento favorito.

*TV Services* - Tu entretenimiento sin límites
        """.strip()
        
        return message


# Instancia global del servicio de notificaciones
notification_service = NotificationService()
