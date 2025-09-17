import requests
import logging
from django.conf import settings
from subscriptions.models import NotificationLog
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Servicio para enviar notificaciones por WhatsApp usando WaSender API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'WASENDER_API_KEY', '')
        self.session_id = getattr(settings, 'WASENDER_SESSION_ID', '')
        self.webhook_url = getattr(settings, 'WASENDER_WEBHOOK_URL', '')
        self.base_url = 'https://wasenderapi.com/api'
        
    def send_expiration_notification(self, subscription, days_notice):
        """
        Enviar notificación de vencimiento por WhatsApp
        
        Args:
            subscription: Instancia de Subscription
            days_notice: Días de aviso antes del vencimiento
            
        Returns:
            dict: Resultado del envío
        """
        try:
            # Limpiar número de teléfono
            phone_number = self._clean_phone_number(subscription.cliente.telefono)
            
            # Generar mensaje personalizado
            message = self._generate_expiration_message(subscription, days_notice)
            
            # Determinar tipo de notificación
            notification_type = self._get_notification_type(days_notice)
            
            # Crear registro de notificación
            notification_log = NotificationLog.objects.create(
                subscription=subscription,
                notification_type=notification_type,
                status=NotificationLog.NotificationStatus.PENDING,
                phone_number=phone_number,
                message_content=message,
                days_notice=days_notice
            )
            
            # Enviar mensaje
            result = self._send_whatsapp_message(phone_number, message)
            
            if result['success']:
                notification_log.mark_as_sent(result.get('api_response'))
                logger.info(f"Notificación enviada exitosamente a {phone_number}")
                return {
                    'success': True,
                    'message': 'Notificación enviada exitosamente',
                    'notification_id': notification_log.id
                }
            else:
                notification_log.mark_as_failed(result.get('error', 'Error desconocido'))
                logger.error(f"Error enviando notificación a {phone_number}: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Error desconocido')
                }
                
        except Exception as e:
            logger.error(f"Error en send_expiration_notification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_whatsapp_message(self, phone_number, message):
        """
        Enviar mensaje por WhatsApp usando WaSender API
        
        Args:
            phone_number: Número de teléfono limpio
            message: Mensaje a enviar
            
        Returns:
            dict: Resultado del envío
        """
        try:
            url = f"{self.base_url}/send"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'session_id': self.session_id,
                'phone': phone_number,
                'message': message
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('success'):
                return {
                    'success': True,
                    'api_response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Error en API de WhatsApp'),
                    'api_response': response_data
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Timeout en la conexión con WaSender API'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
    
    def _clean_phone_number(self, phone):
        """
        Limpiar y formatear número de teléfono
        
        Args:
            phone: Número de teléfono original
            
        Returns:
            str: Número limpio
        """
        if not phone:
            return ''
        
        # Remover espacios, guiones y paréntesis
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Si no empieza con código de país, agregar Ecuador (+593)
        if not clean_phone.startswith('593') and len(clean_phone) >= 9:
            clean_phone = '593' + clean_phone[-9:]
        
        return clean_phone
    
    def _generate_expiration_message(self, subscription, days_notice):
        """
        Generar mensaje personalizado según días de aviso
        
        Args:
            subscription: Instancia de Subscription
            days_notice: Días de aviso
            
        Returns:
            str: Mensaje personalizado
        """
        cliente_name = subscription.cliente.nombre_completo
        service_name = subscription.service.nombre_mostrar
        end_date = subscription.end_date.strftime('%d de %B, %Y')
        price = subscription.price
        
        if days_notice == 0:
            # Vence hoy - mensaje urgente
            message = f"""🚨 ¡URGENTE! Hola {cliente_name}

Tu suscripción a {service_name} vence ¡HOY!
📅 Vence: Hoy, {end_date}
💰 Precio renovación: ${price}

⚡ ¡Renueva AHORA para no perder el servicio!

Responde este mensaje inmediatamente.

¡Gracias por confiar en TV Services! 🎬"""
        
        elif days_notice == 1:
            # Vence mañana
            message = f"""⚠️ Hola {cliente_name}

Tu suscripción a {service_name} vence MAÑANA
📅 Vence: {end_date}
💰 Precio renovación: ${price}
⏰ Queda: 1 día

¡No te quedes sin tu entretenimiento favorito!

Para renovar, responde este mensaje.

¡Gracias por confiar en TV Services! 🎬"""
        
        elif days_notice <= 3:
            # Vence en pocos días
            message = f"""🔔 Hola {cliente_name}

Tu suscripción a {service_name} está por vencer:
📅 Vence: {end_date}
💰 Precio renovación: ${price}
⏰ Quedan: {days_notice} días

Para renovar, responde este mensaje o contacta con nosotros.

¡Gracias por confiar en TV Services! 🎬"""
        
        else:
            # Aviso temprano (7+ días)
            message = f"""📅 Hola {cliente_name}

Recordatorio: Tu suscripción a {service_name} vence pronto:
📅 Vence: {end_date}
💰 Precio renovación: ${price}
⏰ Quedan: {days_notice} días

Tienes tiempo suficiente para renovar sin interrupciones.

Para renovar, responde este mensaje.

¡Gracias por confiar en TV Services! 🎬"""
        
        return message
    
    def _get_notification_type(self, days_notice):
        """
        Determinar tipo de notificación según días de aviso
        
        Args:
            days_notice: Días de aviso
            
        Returns:
            str: Tipo de notificación
        """
        # Por ahora solo usamos EXPIRATION_WARNING para todos los casos
        return NotificationLog.NotificationType.EXPIRATION_WARNING
