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
        self.base_url = 'https://api.wasender.com'
        
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
        Prueba diferentes endpoints hasta encontrar uno que funcione
        
        Args:
            phone_number: Número de teléfono limpio
            message: Mensaje a enviar
            
        Returns:
            dict: Resultado del envío
        """
        
        # Modo de simulación para pruebas (si no hay API key)
        if not self.api_key or self.api_key == 'test' or len(self.api_key) < 10:
            logger.info(f"MODO SIMULACIÓN: WhatsApp a {phone_number}")
            logger.info(f"MENSAJE: {message[:100]}...")
            return {
                'success': True,
                'api_response': {
                    'message_id': 'sim_' + str(hash(phone_number + message))[:8],
                    'status': 'sent',
                    'simulation': True
                },
                'endpoint_used': 'simulation_mode'
            }
        # Configuración correcta de WaSender API
        api_configs = [
            {
                'url': 'https://wasenderapi.com/api/send-message',
                'data': {
                    'to': phone_number,
                    'message': message,
                    'session_id': self.session_id
                }
            }
        ]
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        last_error = None
        
        for config in api_configs:
            try:
                logger.info(f"Intentando enviar WhatsApp via: {config['url']}")
                
                response = requests.post(
                    config['url'], 
                    headers=headers, 
                    json=config['data'], 
                    timeout=30
                )
                
                # Intentar parsear JSON
                try:
                    response_data = response.json()
                except:
                    response_data = {'raw_response': response.text}
                
                logger.info(f"Respuesta de {config['url']}: {response.status_code} - {response_data}")
                
                # Verificar si fue exitoso
                if response.status_code == 200:
                    # Diferentes formas de verificar éxito según la API
                    success_indicators = [
                        response_data.get('success') == True,
                        response_data.get('status') == 'success',
                        'sent' in str(response_data).lower(),
                        'message_id' in response_data,
                        'id' in response_data
                    ]
                    
                    if any(success_indicators) or response.status_code == 200:
                        return {
                            'success': True,
                            'api_response': response_data,
                            'endpoint_used': config['url']
                        }
                
                last_error = response_data.get('message', f'HTTP {response.status_code}')
                
            except requests.exceptions.Timeout:
                last_error = f'Timeout en {config["url"]}'
                logger.warning(last_error)
                continue
            except requests.exceptions.RequestException as e:
                last_error = f'Error de conexión en {config["url"]}: {str(e)}'
                logger.warning(last_error)
                continue
            except Exception as e:
                last_error = f'Error inesperado en {config["url"]}: {str(e)}'
                logger.error(last_error)
                continue
        
        # Si llegamos aquí, todos los endpoints fallaron
        return {
            'success': False,
            'error': f'Todos los endpoints fallaron. Último error: {last_error}'
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
