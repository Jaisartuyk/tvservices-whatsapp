from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta

class Cliente(models.Model):
    """
    Modelo para gestionar clientes en el sistema.
    Los usuarios de la aplicación pueden crear y gestionar múltiples clientes.
    """
    
    # Relación con el usuario que creó/administra este cliente
    creado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clientes_creados',
        verbose_name='Creado por'
    )
    
    # Información personal
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')
    email = models.EmailField(verbose_name='Correo electrónico', blank=True, null=True)
    
    # Información de contacto
    telefono = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="El número de teléfono debe tener el formato: '+999999999'. Hasta 15 dígitos."
            )
        ],
        blank=True,
        null=True,
        verbose_name='Teléfono',
        help_text='Número de teléfono del cliente con código de país'
    )
    
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de nacimiento')
    
    # Información adicional
    notas = models.TextField(blank=True, null=True, verbose_name='Notas adicionales')
    is_active = models.BooleanField(default=True, verbose_name='Cliente activo')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellidos', 'nombres']
        permissions = [
            ('can_manage_clients', 'Puede gestionar clientes'),
        ]
    
    def __str__(self):
        return f"{self.nombre_completo}"
    
    @property
    def nombre_completo(self):
        """Devuelve el nombre completo del cliente"""
        return f"{self.nombres} {self.apellidos}".strip()
    
    @property
    def suscripciones_activas(self):
        """Devuelve las suscripciones activas del cliente"""
        return self.subscriptions.filter(is_active=True)
    
    @property
    def total_gastado(self):
        """Calcula el total gastado por el cliente en suscripciones"""
        return self.subscriptions.aggregate(total=Sum('price'))['total'] or 0
    
    def get_absolute_url(self):
        """URL para ver el detalle del cliente"""
        from django.urls import reverse
        return reverse('admin:subscriptions_cliente_change', args=[self.id])
    
    def save(self, *args, **kwargs):
        # Asegurar que el correo electrónico esté en minúsculas
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)


# Señal para crear automáticamente un perfil de cliente cuando se crea un usuario
@receiver(post_save, sender=User)
def crear_o_actualizar_cliente(sender, instance, created, **kwargs):
    """Crea o actualiza el perfil de cliente cuando se guarda un usuario"""
    if created:
        # Si es un nuevo usuario, creamos el perfil de cliente
        Cliente.objects.create(
            creado_por=instance,
            nombres=instance.first_name or 'Usuario',
            apellidos=instance.last_name or 'Nuevo',
            email=instance.email
        )
        
        # Asignamos al grupo de Clientes si no es superusuario
        if not instance.is_superuser:
            grupo_clientes, _ = Group.objects.get_or_create(name='Clientes')
            instance.groups.add(grupo_clientes)
    else:
        # Si el usuario ya existe, actualizamos el perfil si existe
        try:
            cliente = instance.clientes_creados.first()
            if cliente:
                cliente.email = instance.email
                if instance.first_name:
                    cliente.nombres = instance.first_name
                if instance.last_name:
                    cliente.apellidos = instance.last_name
                cliente.save()
        except Exception as e:
            # Si hay algún error, lo registramos pero no detenemos el flujo
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error al actualizar cliente: {str(e)}')


class CategoriaServicio(models.Model):
    """Categorías para organizar los servicios de streaming"""
    nombre = models.CharField(max_length=50, unique=True, verbose_name=_('Nombre'))
    descripcion = models.TextField(blank=True, verbose_name=_('Descripción'))
    icono = models.CharField(
        max_length=50, 
        blank=True, 
        help_text=_('Clase de ícono de Bootstrap Icons (ej: netflix, spotify, etc.)'),
        verbose_name=_('Ícono')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Activa'))
    orden = models.PositiveIntegerField(default=0, verbose_name=_('Orden'))
    
    class Meta:
        verbose_name = _('Categoría de servicio')
        verbose_name_plural = _('Categorías de servicios')
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class Service(models.Model):
    """Modelo para los servicios de streaming disponibles"""
    
    class TipoSuscripcion(models.TextChoices):
        MENSUAL = 'monthly', _('Mensual')
        TRIMESTRAL = 'quarterly', _('Trimestral')
        SEMESTRAL = 'semiannual', _('Semestral')
        ANUAL = 'annual', _('Anual')
    
    # Información básica
    nombre = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name=_('Nombre interno')
    )
    
    nombre_mostrar = models.CharField(
        max_length=100, 
        verbose_name=_('Nombre para mostrar')
    )
    
    descripcion = models.TextField(
        blank=True, 
        verbose_name=_('Descripción')
    )
    
    # Categorización
    categoria = models.ForeignKey(
        CategoriaServicio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='servicios',
        verbose_name=_('Categoría')
    )
    
    # Precios
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Precio base')
    )
    
    max_dispositivos = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Máximo de dispositivos'),
        help_text=_('Número máximo de dispositivos permitidos para este servicio')
    )
    
    tipo_suscripcion = models.CharField(
        max_length=20,
        choices=TipoSuscripcion.choices,
        default=TipoSuscripcion.MENSUAL,
        verbose_name=_('Tipo de suscripción')
    )
    
    # Estado y metadatos
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activo')
    )
    
    # Detalles adicionales
    fecha_lanzamiento = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de lanzamiento')
    )
    
    pais_origen = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('País de origen')
    )
    
    calidad = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Calidad de video'),
        help_text=_('Ej: 4K, 1080p, 720p')
    )
    
    sitio_web = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Sitio web oficial')
    )
    
    idiomas = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Idiomas disponibles'),
        help_text=_('Separe los idiomas con comas')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última actualización')
    )
    
    # Imágenes e iconos
    icono = models.CharField(
        max_length=50, 
        blank=True, 
        help_text=_('Clase de ícono de Bootstrap Icons (ej: netflix, spotify, etc.)'),
        verbose_name=_('Ícono')
    )
    
    imagen = models.ImageField(
        upload_to='servicios/',
        blank=True,
        null=True,
        verbose_name=_('Imagen destacada')
    )
    
    # Métodos
    def __str__(self):
        return self.nombre_mostrar
    
    class Meta:
        verbose_name = _('Servicio')
        verbose_name_plural = _('Servicios')
        ordering = ['categoria__nombre', 'nombre_mostrar']
    
    @property
    def precio_formateado(self):
        """Devuelve el precio formateado como moneda"""
        return f"${self.precio_base:,.2f}"
        
    @property
    def get_tipo_suscripcion_display(self):
        """Devuelve el nombre legible del tipo de suscripción"""
        return dict(self.TipoSuscripcion.choices).get(self.tipo_suscripcion, '')
    
    @property
    def tipo_suscripcion_display(self):
        """Devuelve el nombre legible del tipo de suscripción"""
        return dict(self.TipoSuscripcion.choices).get(self.tipo_suscripcion, '')
    
    def tiene_suscripciones_activas(self):
        """Indica si el servicio tiene suscripciones activas"""
        return self.subscriptions.filter(is_active=True).exists()

class Subscription(models.Model):
    """Modelo para las suscripciones de clientes a servicios de streaming"""
    
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'pending', _('Pendiente de pago')
        PAGADO = 'paid', _('Pagado')
        CANCELADO = 'cancelled', _('Cancelado')
        EXPIRADO = 'expired', _('Expirado')
        FALLIDO = 'failed', _('Fallido')
    
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'cash', _('Efectivo')
        TRANSFERENCIA = 'transfer', _('Transferencia bancaria')
        TARJETA = 'card', _('Tarjeta de crédito/débito')
        OTRO = 'other', _('Otro método')
    
    # Relaciones
    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('Cliente')
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_('Servicio')
    )
    
    # Información de la suscripción
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Precio pagado')
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
        default=MetodoPago.EFECTIVO,
        verbose_name=_('Método de pago')
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
        verbose_name=_('Estado del pago')
    )
    
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de pago')
    )
    
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Referencia de pago')
    )
    
    start_date = models.DateField(
        verbose_name=_('Fecha de inicio')
    )
    
    end_date = models.DateField(
        verbose_name=_('Fecha de expiración')
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de cancelación')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activa')
    )
    
    # Información adicional
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notas adicionales')
    )
    
    # Campos para Stripe
    stripe_customer_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='ID del cliente en Stripe'
    )
    
    stripe_subscription_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='ID de la suscripción en Stripe'
    )
    
    stripe_payment_intent = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='ID del intento de pago en Stripe'
    )
    
    # Auditoría
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('Última actualización')
    )
    
    class Meta:
        verbose_name = _('Suscripción')
        verbose_name_plural = _('Suscripciones')
        ordering = ['-created_at']
        permissions = [
            ('can_manage_subscriptions', 'Puede gestionar suscripciones'),
        ]
    
    def __str__(self):
        return f"{self.cliente.nombre_completo} - {self.service.nombre_mostrar} (${self.price})"
    
    @property
    def days_remaining(self):
        """Devuelve los días restantes para la expiración de la suscripción"""
        if not self.is_active:
            return 0
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    @property
    def dias_restantes(self):
        """Alias en español para days_remaining"""
        return self.days_remaining
    
    @property
    def is_expiring_soon(self):
        """Indica si la suscripción está por vencer (menos de 7 días)"""
        return self.is_active and 0 < self.days_remaining <= 7
    
    def cancel(self, reason=None):
        """Cancela la suscripción"""
        self.is_active = False
        self.cancelled_at = timezone.now()
        if reason:
            self.notes = f"{self.notes or ''}\n---\nCancelación: {reason}"
        self.save()
    
    def renew(self, months=1, price=None):
        """Renueva la suscripción por la cantidad de meses especificada"""
        today = timezone.now().date()
        
        # Si la suscripción ya expiró, la renovamos desde hoy
        if today > self.end_date:
            self.start_date = today
            self.end_date = today + timezone.timedelta(days=30 * months)
        else:
            # Si aún no expira, extendemos la fecha de expiración
            self.end_date += timezone.timedelta(days=30 * months)
        
        # Actualizamos el precio si se especificó uno
        if price is not None:
            self.price = price
        
        # Reactivamos la suscripción si estaba inactiva
        if not self.is_active:
            self.is_active = True
            self.cancelled_at = None
        
        self.save()
        return self
    
    def save(self, *args, **kwargs):
        # Si es una nueva suscripción, establecer la fecha de inicio como hoy
        if not self.pk:
            self.start_date = timezone.now().date()
            
            # Si no hay fecha de fin, establecer según el tipo de suscripción
            if not self.end_date:
                if self.service.tipo_suscripcion == Service.TipoSuscripcion.TRIMESTRAL:
                    self.end_date = self.start_date + timedelta(days=90)
                elif self.service.tipo_suscripcion == Service.TipoSuscripcion.ANUAL:
                    self.end_date = self.start_date + timedelta(days=365)
                else:  # Mensual por defecto
                    self.end_date = self.start_date + timedelta(days=30)
        
        # Si se está actualizando el estado de pago a 'paid', registrar la fecha de pago
        if self.pk and self.payment_status == self.EstadoPago.PAGADO and not self.payment_date:
            self.payment_date = timezone.now()
            
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Modelo para registrar los pagos de las suscripciones
    """
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'pending', _('Pendiente')
        COMPLETADO = 'completed', _('Completado')
        FALLIDO = 'failed', _('Fallido')
        REEMBOLSADO = 'refunded', _('Reembolsado')
        CANCELADO = 'cancelled', _('Cancelado')
    
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'efectivo', _('Efectivo')
        TRANSFERENCIA = 'transferencia', _('Transferencia Bancaria')
        TARJETA = 'tarjeta', _('Tarjeta de Crédito/Débito')
        PAYPAL = 'paypal', _('PayPal')
        OTRO = 'otro', _('Otro')
    
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Suscripción')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Monto')
    )
    payment_method = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
        verbose_name=_('Método de pago')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
        verbose_name=_('Estado del pago')
    )
    payment_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Fecha de pago')
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Referencia/Número de operación')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notas adicionales')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última actualización')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pagos_creados',
        verbose_name=_('Creado por')
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos_actualizados',
        verbose_name=_('Actualizado por')
    )

    class Meta:
        verbose_name = _('Pago')
        verbose_name_plural = _('Pagos')
        ordering = ['-payment_date']
        permissions = [
            ('can_view_payment', 'Puede ver pagos'),
            ('can_add_payment', 'Puede agregar pagos'),
            ('can_change_payment', 'Puede cambiar pagos'),
            ('can_delete_payment', 'Puede eliminar pagos'),
        ]
    
    def __str__(self):
        return f'Pago de ${self.amount} - {self.get_payment_status_display()} ({self.payment_date.strftime("%d/%m/%Y")})'
    
    def save(self, *args, **kwargs):
        # Actualizar la fecha de modificación
        self.updated_at = timezone.now()
        
        # Si el pago se marca como completado, actualizar la suscripción
        if self.payment_status == self.EstadoPago.COMPLETADO and not self.subscription.payment_date:
            self.subscription.payment_status = 'paid'
            self.subscription.payment_date = self.payment_date
            self.subscription.save()
            
        super().save(*args, **kwargs)


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
