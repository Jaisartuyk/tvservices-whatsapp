from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from subscriptions.services import WhatsAppService, NotificationService
import logging

logger = logging.getLogger('subscriptions.management')

class Command(BaseCommand):
    help = 'Prueba la configuración del servicio de WhatsApp'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            help='Número de teléfono para enviar mensaje de prueba (ej: 573001234567)'
        )
        parser.add_argument(
            '--message',
            type=str,
            default='🧪 Mensaje de prueba desde TV Services. ¡El sistema de notificaciones funciona correctamente!',
            help='Mensaje personalizado para enviar'
        )

    def handle(self, *args, **options):
        self.stdout.write('🔧 Probando configuración del servicio de WhatsApp...\n')
        
        # Verificar configuración
        self._check_configuration()
        
        # Probar servicio básico
        self._test_whatsapp_service()
        
        # Si se proporciona un teléfono, enviar mensaje de prueba
        if options['phone']:
            self._send_test_message(options['phone'], options['message'])
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Pruebas completadas. Revisa los logs para más detalles.')
        )

    def _check_configuration(self):
        """Verifica la configuración del sistema"""
        self.stdout.write('📋 Verificando configuración...')
        
        # Verificar variables de entorno
        api_key = getattr(settings, 'WASENDER_API_KEY', '')
        instance_id = getattr(settings, 'WASENDER_INSTANCE_ID', '')
        api_url = getattr(settings, 'WASENDER_API_URL', '')
        
        if not api_key:
            self.stdout.write(
                self.style.ERROR('❌ WASENDER_API_KEY no está configurado')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ API Key configurado: {api_key[:10]}...')
            )
        
        if not instance_id:
            self.stdout.write(
                self.style.ERROR('❌ WASENDER_INSTANCE_ID no está configurado')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Instance ID configurado: {instance_id}')
            )
        
        self.stdout.write(f'🌐 API URL: {api_url}')
        
        # Verificar configuración de notificaciones
        notification_settings = getattr(settings, 'NOTIFICATION_SETTINGS', {})
        enabled = notification_settings.get('ENABLE_WHATSAPP_NOTIFICATIONS', False)
        
        if enabled:
            self.stdout.write(
                self.style.SUCCESS('✅ Notificaciones de WhatsApp habilitadas')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Notificaciones de WhatsApp deshabilitadas')
            )
        
        days_notice = notification_settings.get('EXPIRATION_DAYS_NOTICE', [])
        self.stdout.write(f'📅 Días de aviso configurados: {days_notice}')

    def _test_whatsapp_service(self):
        """Prueba la inicialización del servicio"""
        self.stdout.write('\n🔌 Probando servicio de WhatsApp...')
        
        try:
            whatsapp_service = WhatsAppService()
            self.stdout.write('✅ Servicio de WhatsApp inicializado correctamente')
            
            # Probar limpieza de números
            test_numbers = [
                '3001234567',      # Número colombiano sin código
                '+573001234567',   # Número con código internacional
                '57 300 123 4567', # Número con espacios
                '(300) 123-4567',  # Número con formato
                '1234567',         # Número fijo sin código de área
            ]
            
            self.stdout.write('\n📞 Probando limpieza de números de teléfono:')
            for number in test_numbers:
                cleaned = whatsapp_service._clean_phone_number(number)
                status = '✅' if cleaned else '❌'
                self.stdout.write(f'  {status} {number} → {cleaned}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error inicializando servicio: {str(e)}')
            )

    def _send_test_message(self, phone_number, message):
        """Envía un mensaje de prueba"""
        self.stdout.write(f'\n📱 Enviando mensaje de prueba a {phone_number}...')
        
        try:
            whatsapp_service = WhatsAppService()
            result = whatsapp_service.send_message(phone_number, message)
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Mensaje enviado exitosamente!')
                )
                self.stdout.write(f'📊 Respuesta: {result.get("data", {})}')
            else:
                error = result.get('error', 'Error desconocido')
                self.stdout.write(
                    self.style.ERROR(f'❌ Error enviando mensaje: {error}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error inesperado: {str(e)}')
            )

    def _test_notification_service(self):
        """Prueba el servicio de notificaciones (sin envío real)"""
        self.stdout.write('\n🔔 Probando servicio de notificaciones...')
        
        try:
            notification_service = NotificationService()
            self.stdout.write('✅ Servicio de notificaciones inicializado correctamente')
            
            # Aquí podrías agregar más pruebas específicas del servicio de notificaciones
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error inicializando servicio de notificaciones: {str(e)}')
            )
