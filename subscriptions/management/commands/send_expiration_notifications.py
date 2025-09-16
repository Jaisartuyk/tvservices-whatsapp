from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta
from subscriptions.models import Subscription
from subscriptions.services import notification_service
import logging
import time

logger = logging.getLogger('subscriptions.management')

class Command(BaseCommand):
    help = 'Envía notificaciones de WhatsApp para suscripciones próximas a vencer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Días antes del vencimiento para enviar notificaciones (default: 1)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo de prueba sin enviar mensajes reales'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar envío incluso si las notificaciones están deshabilitadas'
        )

    def handle(self, *args, **options):
        # Verificar si las notificaciones están habilitadas
        notification_settings = getattr(settings, 'NOTIFICATION_SETTINGS', {})
        if not options['force'] and not notification_settings.get('ENABLE_WHATSAPP_NOTIFICATIONS', False):
            self.stdout.write(
                self.style.WARNING('Las notificaciones de WhatsApp están deshabilitadas')
            )
            return

        days_notice = options['days']
        dry_run = options['dry_run']
        
        # Calcular la fecha objetivo
        target_date = date.today() + timedelta(days=days_notice)
        
        self.stdout.write(f'Buscando suscripciones que vencen el {target_date.strftime("%d/%m/%Y")}...')
        
        # Obtener suscripciones que vencen en la fecha objetivo
        expiring_subscriptions = Subscription.objects.filter(
            end_date=target_date,
            is_active=True,
            cliente__telefono__isnull=False,
            cliente__telefono__gt='',
            cliente__is_active=True
        ).select_related('cliente', 'service')
        
        total_subscriptions = expiring_subscriptions.count()
        
        if total_subscriptions == 0:
            self.stdout.write(
                self.style.SUCCESS(f'No hay suscripciones que venzan el {target_date.strftime("%d/%m/%Y")}')
            )
            return
        
        self.stdout.write(f'Encontradas {total_subscriptions} suscripciones para notificar')
        
        # Contadores para estadísticas
        sent_count = 0
        error_count = 0
        
        # Enviar notificaciones
        for subscription in expiring_subscriptions:
            try:
                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Notificaría a {subscription.cliente.nombre_completo} '
                        f'sobre {subscription.service.nombre_mostrar}'
                    )
                    sent_count += 1
                else:
                    # Enviar notificación real
                    result = notification_service.send_expiration_notification(
                        subscription, 
                        days_notice
                    )
                    
                    if result['success']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Notificación enviada a {subscription.cliente.nombre_completo} '
                                f'({subscription.cliente.telefono})'
                            )
                        )
                        sent_count += 1
                        
                        # Registrar la notificación (opcional: crear modelo NotificationLog)
                        self._log_notification(subscription, days_notice, True)
                        
                        # Esperar 5 segundos para respetar rate limiting de WaSender API
                        if not dry_run and sent_count < total_subscriptions:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⏳ Esperando 5 segundos para respetar límites de API...'
                                )
                            )
                            time.sleep(5)
                        
                    else:
                        error_msg = result.get('error', 'Error desconocido')
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Error enviando a {subscription.cliente.nombre_completo}: {error_msg}'
                            )
                        )
                        error_count += 1
                        
                        # Registrar el error
                        self._log_notification(subscription, days_notice, False, error_msg)
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error inesperado con {subscription.cliente.nombre_completo}: {str(e)}'
                    )
                )
                error_count += 1
                logger.error(f'Error inesperado enviando notificación: {str(e)}')
        
        # Mostrar resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'RESUMEN DE NOTIFICACIONES')
        self.stdout.write('='*50)
        self.stdout.write(f'Total de suscripciones: {total_subscriptions}')
        self.stdout.write(f'Notificaciones enviadas: {sent_count}')
        self.stdout.write(f'Errores: {error_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n[MODO DE PRUEBA] No se enviaron mensajes reales'))
        
        if error_count == 0:
            self.stdout.write(self.style.SUCCESS('\n¡Todas las notificaciones se enviaron exitosamente!'))
        elif sent_count > 0:
            self.stdout.write(self.style.WARNING(f'\nSe enviaron {sent_count} notificaciones con {error_count} errores'))
        else:
            self.stdout.write(self.style.ERROR('\n¡No se pudo enviar ninguna notificación!'))
    
    def _log_notification(self, subscription, days_notice, success, error_msg=None):
        """
        Registra el resultado de la notificación en los logs
        En el futuro se puede crear un modelo NotificationLog para persistir esto
        """
        status = 'SUCCESS' if success else 'ERROR'
        message = f'Notification {status} - Cliente: {subscription.cliente.nombre_completo}, ' \
                 f'Servicio: {subscription.service.nombre_mostrar}, ' \
                 f'Días de aviso: {days_notice}'
        
        if error_msg:
            message += f', Error: {error_msg}'
        
        if success:
            logger.info(message)
        else:
            logger.error(message)
