from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    Service, Subscription, Cliente, 
    CategoriaServicio, Payment, NotificationLog
)


class ServiceAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Service"""
    list_display = ('nombre_mostrar', 'categoria', 'precio_base_formateado', 'tipo_suscripcion', 'is_active', 'fecha_lanzamiento')
    list_filter = ('is_active', 'categoria', 'tipo_suscripcion')
    search_fields = ('nombre', 'nombre_mostrar', 'descripcion')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'nombre_mostrar', 'descripcion', 'categoria', 'is_active')
        }),
        ('Configuración de Precios', {
            'fields': ('precio_base', 'tipo_suscripcion', 'max_dispositivos')
        }),
        ('Detalles Técnicos', {
            'fields': ('calidad', 'idiomas', 'pais_origen', 'fecha_lanzamiento', 'sitio_web', 'icono')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Si es un nuevo objeto
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

    def precio_base_formateado(self, obj):
        return f"${obj.precio_base:,.2f}"
    precio_base_formateado.short_description = 'Precio'
    precio_base_formateado.admin_order_field = 'precio_base'


class SubscriptionAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Subscription"""
    list_display = ('id', 'cliente_link', 'service_link', 'estado_pago', 'fecha_inicio', 'fecha_fin', 'dias_restantes')
    list_filter = ('payment_status', 'service', 'start_date', 'end_date')
    search_fields = ('cliente__nombres', 'cliente__apellidos', 'service__nombre_mostrar')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('cliente', 'service', 'price', 'is_active')
        }),
        ('Información de Pago', {
            'fields': ('payment_method', 'payment_status', 'payment_date', 'payment_reference')
        }),
        ('Período de Suscripción', {
            'fields': ('start_date', 'end_date', 'cancelled_at')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def cliente_link(self, obj):
        url = reverse('admin:subscriptions_cliente_change', args=[obj.cliente.id])
        return format_html('<a href="{}">{}</a>', url, obj.cliente.nombre_completo)
    cliente_link.short_description = 'Cliente'
    cliente_link.admin_order_field = 'cliente__nombres'
    
    def service_link(self, obj):
        url = reverse('admin:subscriptions_service_change', args=[obj.service.id])
        return format_html('<a href="{}">{}</a>', url, obj.service.nombre_mostrar)
    service_link.short_description = 'Servicio'
    service_link.admin_order_field = 'service__nombre_mostrar'
    
    def estado_pago(self, obj):
        return obj.get_payment_status_display()
    estado_pago.short_description = 'Estado Pago'
    estado_pago.admin_order_field = 'payment_status'
    
    def fecha_inicio(self, obj):
        return obj.start_date
    fecha_inicio.short_description = 'Inicio'
    fecha_inicio.admin_order_field = 'start_date'
    
    def fecha_fin(self, obj):
        return obj.end_date
    fecha_fin.short_description = 'Fin'
    fecha_fin.admin_order_field = 'end_date'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es una nueva suscripción
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ClienteAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Cliente"""
    list_display = ('nombre_completo', 'email', 'telefono', 'fecha_registro', 'is_active')
    list_filter = ('is_active', 'fecha_registro')
    search_fields = ('nombres', 'apellidos', 'email', 'telefono')
    readonly_fields = ('fecha_registro', 'creado_por')
    list_editable = ('is_active',)
    
    def get_readonly_fields(self, request, obj=None):
        # Hacemos que los campos de solo lectura sean dinámicos
        if obj:  # Si estamos editando un objeto existente
            return self.readonly_fields + ('creado_por',)
        return self.readonly_fields
    
    fieldsets = (
        (None, {
            'fields': ('nombres', 'apellidos', 'email', 'telefono', 'is_active')
        }),
        ('Información Adicional', {
            'fields': ('direccion', 'fecha_nacimiento', 'notas'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('fecha_registro', 'creado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo cliente
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


class CategoriaServicioAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo CategoriaServicio"""
    list_display = ('nombre', 'is_active', 'orden')
    list_editable = ('is_active', 'orden')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('is_active',)


class PaymentAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Payment"""
    list_display = ('id', 'subscription_link', 'monto', 'metodo_pago', 'estado_pago', 'fecha_pago', 'created_by')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('subscription__cliente__nombres', 'subscription__cliente__apellidos', 'reference')
    readonly_fields = ('created_at', 'updated_at')
    
    def subscription_link(self, obj):
        url = reverse('admin:subscriptions_subscription_change', args=[obj.subscription.id])
        return format_html('<a href="{}">Suscripción #{}</a>', url, obj.subscription.id)
    subscription_link.short_description = 'Suscripción'
    
    def monto(self, obj):
        return f"${obj.amount:,.2f}"
    monto.short_description = 'Monto'
    monto.admin_order_field = 'amount'
    
    def metodo_pago(self, obj):
        return obj.get_payment_method_display()
    metodo_pago.short_description = 'Método de Pago'
    metodo_pago.admin_order_field = 'payment_method'
    
    def estado_pago(self, obj):
        return obj.get_payment_status_display()
    estado_pago.short_description = 'Estado'
    estado_pago.admin_order_field = 'payment_status'
    
    def fecha_pago(self, obj):
        return obj.payment_date
    fecha_pago.short_description = 'Fecha Pago'
    fecha_pago.admin_order_field = 'payment_date'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo pago
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class NotificationLogAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo NotificationLog"""
    list_display = (
        'id', 'cliente_name_link', 'service_name_link', 'notification_type', 
        'status', 'phone_number', 'days_notice', 'created_at', 'sent_at'
    )
    list_filter = (
        'notification_type', 'status', 'created_at', 'sent_at', 
        'subscription__service', 'days_notice'
    )
    search_fields = (
        'subscription__cliente__nombres', 'subscription__cliente__apellidos',
        'subscription__service__nombre_mostrar', 'phone_number', 'message_content'
    )
    readonly_fields = (
        'created_at', 'sent_at', 'delivered_at', 'api_response', 
        'cliente_name', 'service_name'
    )
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('subscription', 'notification_type', 'status', 'days_notice')
        }),
        ('Detalles del Envío', {
            'fields': ('phone_number', 'message_content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('api_response', 'error_message', 'retry_count', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def cliente_name_link(self, obj):
        """Enlace al cliente"""
        if obj.subscription and obj.subscription.cliente:
            url = reverse('admin:subscriptions_cliente_change', args=[obj.subscription.cliente.pk])
            return format_html('<a href="{}">{}</a>', url, obj.cliente_name)
        return '-'
    cliente_name_link.short_description = 'Cliente'
    cliente_name_link.admin_order_field = 'subscription__cliente__nombres'
    
    def service_name_link(self, obj):
        """Enlace al servicio"""
        if obj.subscription and obj.subscription.service:
            url = reverse('admin:subscriptions_service_change', args=[obj.subscription.service.pk])
            return format_html('<a href="{}">{}</a>', url, obj.service_name)
        return '-'
    service_name_link.short_description = 'Servicio'
    service_name_link.admin_order_field = 'subscription__service__nombre_mostrar'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'subscription__cliente', 'subscription__service', 'created_by'
        )
    
    def has_add_permission(self, request):
        """Solo permitir agregar a superusuarios"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir cambios limitados"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar"""
        return request.user.is_superuser


# Registrar los modelos con sus respectivas configuraciones
admin.site.register(Service, ServiceAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(CategoriaServicio, CategoriaServicioAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(NotificationLog, NotificationLogAdmin)
