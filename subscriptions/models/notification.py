from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class NotificationLog(models.Model):
    """
    Modelo para registrar el historial de notificaciones enviadas
    """
    
    class NotificationType(models.TextChoices):
        EXPIRATION_WARNING = 'expiration_warning', 'Aviso de vencimiento'
        RENEWAL_CONFIRMATION = 'renewal_confirmation', 'Confirmación de renovación'
        PAYMENT_REMINDER = 'payment_reminder', 'Recordatorio de pago'
    
    class NotificationStatus(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        SENT = 'sent', 'Enviado'
        FAILED = 'failed', 'Fallido'
        DELIVERED = 'delivered', 'Entregado'
        READ = 'read', 'Leído'
    
    # Relaciones
    subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Suscripción'
    )
    
    # Información de la notificación
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        verbose_name='Tipo de notificación'
    )
    
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name='Estado'
    )
    
    # Detalles del envío
    phone_number = models.CharField(
        max_length=20,
        verbose_name='Número de teléfono'
    )
    
    message_content = models.TextField(
        verbose_name='Contenido del mensaje'
    )
    
    days_notice = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Días de aviso',
        help_text='Días antes del vencimiento (solo para avisos de vencimiento)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de envío'
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de entrega'
    )
    
    # Información de respuesta de la API
    api_response = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Respuesta de la API'
    )
    
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='Mensaje de error'
    )
    
    # Metadatos
    retry_count = models.IntegerField(
        default=0,
        verbose_name='Intentos de reenvío'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Registro de Notificación'
        verbose_name_plural = 'Registros de Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', 'notification_type']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['phone_number', 'sent_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.subscription.cliente.nombre_completo} ({self.get_status_display()})"
    
    def mark_as_sent(self, api_response=None):
        """Marca la notificación como enviada"""
        self.status = self.NotificationStatus.SENT
        self.sent_at = timezone.now()
        if api_response:
            self.api_response = api_response
        self.save()
    
    def mark_as_failed(self, error_message):
        """Marca la notificación como fallida"""
        self.status = self.NotificationStatus.FAILED
        self.error_message = error_message
        self.save()
    
    def mark_as_delivered(self):
        """Marca la notificación como entregada"""
        self.status = self.NotificationStatus.DELIVERED
        self.delivered_at = timezone.now()
        self.save()
    
    @property
    def cliente_name(self):
        """Nombre del cliente asociado"""
        return self.subscription.cliente.nombre_completo
    
    @property
    def service_name(self):
        """Nombre del servicio asociado"""
        return self.subscription.service.nombre_mostrar
