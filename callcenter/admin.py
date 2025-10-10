"""
Configuración del Admin para Call Center IA
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Avg
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Operador, Producto, Lead, Conversacion, 
    LlamadaIA, Venta
)


@admin.register(Operador)
class OperadorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono_atencion', 'color_badge', 'is_active', 'orden', 'total_productos']
    list_filter = ['is_active']
    search_fields = ['nombre']
    list_editable = ['orden', 'is_active']
    ordering = ['orden', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'logo', 'sitio_web', 'telefono_atencion')
        }),
        ('Diseño', {
            'fields': ('color_principal', 'orden')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px;">{}</span>',
            obj.color_principal,
            obj.nombre
        )
    color_badge.short_description = 'Color'
    
    def total_productos(self, obj):
        count = obj.productos.filter(is_active=True).count()
        return format_html('<strong>{}</strong> productos', count)
    total_productos.short_description = 'Productos Activos'


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_plan', 'operador', 'tipo', 'precio_badge', 
        'velocidad_mbps', 'is_destacado', 'is_active', 'total_ventas'
    ]
    list_filter = ['operador', 'tipo', 'is_active', 'is_destacado']
    search_fields = ['nombre_plan', 'descripcion']
    list_editable = ['is_destacado', 'is_active']
    readonly_fields = ['created_at', 'updated_at', 'precio_con_descuento', 'ahorro_mensual']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('operador', 'tipo', 'nombre_plan', 'descripcion')
        }),
        ('Características', {
            'fields': (
                'velocidad_mbps', 'gigas_datos', 'minutos_llamadas', 
                'canales_tv', 'beneficios', 'restricciones'
            )
        }),
        ('Precios', {
            'fields': (
                'precio_mensual', 'precio_instalacion', 'descuento_porcentaje',
                'precio_con_descuento', 'ahorro_mensual'
            )
        }),
        ('Disponibilidad', {
            'fields': ('zonas_disponibles', 'stock_disponible')
        }),
        ('Estado', {
            'fields': ('is_active', 'is_destacado')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def precio_badge(self, obj):
        precio = obj.precio_con_descuento
        if obj.descuento_porcentaje > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">${:.2f}</span> '
                '<span style="text-decoration: line-through; color: gray;">${:.2f}</span>',
                precio, obj.precio_mensual
            )
        return format_html('<strong>${:.2f}</strong>', precio)
    precio_badge.short_description = 'Precio'
    
    def total_ventas(self, obj):
        count = obj.ventas.count()
        if count > 0:
            return format_html('<strong style="color: green;">{}</strong> ventas', count)
        return '0 ventas'
    total_ventas.short_description = 'Ventas'


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_completo', 'telefono', 'clasificacion_badge', 
        'estado_badge', 'score_badge', 'fuente', 'agente_asignado',
        'ultima_interaccion', 'acciones'
    ]
    list_filter = [
        'clasificacion', 'estado', 'fuente', 'agente_asignado',
        'operador_interes', 'tipo_servicio_interes'
    ]
    search_fields = ['nombre', 'apellido', 'telefono', 'email']
    readonly_fields = [
        'score', 'clasificacion', 'created_at', 'updated_at',
        'ultima_interaccion', 'total_conversaciones', 'total_llamadas'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'telefono', 'email', 'direccion', 'zona')
        }),
        ('Intereses', {
            'fields': (
                'operador_interes', 'producto_interes', 'tipo_servicio_interes',
                'presupuesto_estimado'
            )
        }),
        ('Clasificación y Scoring', {
            'fields': ('score', 'clasificacion', 'estado', 'fuente'),
            'classes': ('wide',)
        }),
        ('Asignación', {
            'fields': ('agente_asignado',)
        }),
        ('Análisis de IA', {
            'fields': ('notas_ia', 'intenciones_detectadas', 'objeciones'),
            'classes': ('collapse',)
        }),
        ('Seguimiento', {
            'fields': (
                'ultima_interaccion', 'proxima_accion', 'fecha_proxima_accion',
                'total_conversaciones', 'total_llamadas'
            )
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Control', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_como_hot', 'marcar_como_warm', 'marcar_como_cold', 'actualizar_scores']
    
    def clasificacion_badge(self, obj):
        colors = {
            'HOT': '#dc3545',
            'WARM': '#ffc107',
            'COLD': '#6c757d'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 5px; font-weight: bold;">{}</span>',
            colors.get(obj.clasificacion, '#6c757d'),
            obj.get_clasificacion_display()
        )
    clasificacion_badge.short_description = 'Clasificación'
    
    def estado_badge(self, obj):
        colors = {
            'NUEVO': '#17a2b8',
            'CONTACTADO': '#007bff',
            'CALIFICADO': '#28a745',
            'NEGOCIANDO': '#ffc107',
            'GANADO': '#28a745',
            'PERDIDO': '#dc3545',
            'SEGUIMIENTO': '#6c757d'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.estado, '#6c757d'),
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def score_badge(self, obj):
        if obj.score >= 80:
            color = '#dc3545'
        elif obj.score >= 50:
            color = '#ffc107'
        else:
            color = '#6c757d'
        
        return format_html(
            '<div style="width: 60px; background-color: #e9ecef; border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; color: white; text-align: center; '
            'padding: 2px; font-weight: bold; font-size: 11px;">{}</div></div>',
            obj.score, color, obj.score
        )
    score_badge.short_description = 'Score'
    
    def total_conversaciones(self, obj):
        count = obj.conversaciones.count()
        return format_html('<strong>{}</strong> conversaciones', count)
    total_conversaciones.short_description = 'Conversaciones'
    
    def total_llamadas(self, obj):
        count = obj.llamadas.count()
        return format_html('<strong>{}</strong> llamadas', count)
    total_llamadas.short_description = 'Llamadas'
    
    def acciones(self, obj):
        return format_html(
            '<a class="button" href="{}">Ver Detalle</a>',
            reverse('admin:callcenter_lead_change', args=[obj.pk])
        )
    acciones.short_description = 'Acciones'
    
    def marcar_como_hot(self, request, queryset):
        queryset.update(clasificacion='HOT', score=90)
        self.message_user(request, f'{queryset.count()} leads marcados como HOT')
    marcar_como_hot.short_description = '🔥 Marcar como HOT'
    
    def marcar_como_warm(self, request, queryset):
        queryset.update(clasificacion='WARM', score=60)
        self.message_user(request, f'{queryset.count()} leads marcados como WARM')
    marcar_como_warm.short_description = '🌡️ Marcar como WARM'
    
    def marcar_como_cold(self, request, queryset):
        queryset.update(clasificacion='COLD', score=30)
        self.message_user(request, f'{queryset.count()} leads marcados como COLD')
    marcar_como_cold.short_description = '❄️ Marcar como COLD'
    
    def actualizar_scores(self, request, queryset):
        for lead in queryset:
            lead.actualizar_score()
        self.message_user(request, f'Scores actualizados para {queryset.count()} leads')
    actualizar_scores.short_description = '🔄 Actualizar Scores'


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = [
        'lead', 'canal', 'tipo', 'sentimiento_badge', 
        'fue_atendido_por_ia', 'agente_humano', 'created_at'
    ]
    list_filter = ['canal', 'tipo', 'sentimiento', 'fue_atendido_por_ia', 'created_at']
    search_fields = ['lead__nombre', 'lead__apellido', 'mensaje_cliente', 'respuesta_sistema']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Lead', {
            'fields': ('lead',)
        }),
        ('Detalles de Conversación', {
            'fields': ('canal', 'tipo', 'duracion_segundos')
        }),
        ('Contenido', {
            'fields': ('mensaje_cliente', 'respuesta_sistema', 'transcripcion')
        }),
        ('Análisis', {
            'fields': (
                'sentimiento', 'intenciones_detectadas', 'objeciones_detectadas',
                'siguiente_accion'
            )
        }),
        ('Agente', {
            'fields': ('fue_atendido_por_ia', 'agente_humano')
        }),
        ('Archivos', {
            'fields': ('audio_url',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def sentimiento_badge(self, obj):
        colors = {
            'POSITIVO': '#28a745',
            'NEUTRAL': '#6c757d',
            'NEGATIVO': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.sentimiento, '#6c757d'),
            obj.get_sentimiento_display()
        )
    sentimiento_badge.short_description = 'Sentimiento'


@admin.register(LlamadaIA)
class LlamadaIAAdmin(admin.ModelAdmin):
    list_display = [
        'lead', 'tipo', 'telefono_destino', 'resultado_badge',
        'duracion_formateada', 'created_at'
    ]
    list_filter = ['tipo', 'resultado', 'created_at']
    search_fields = ['lead__nombre', 'lead__apellido', 'telefono_destino']
    readonly_fields = ['created_at', 'duracion_formateada']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Lead', {
            'fields': ('lead', 'conversacion')
        }),
        ('Detalles de Llamada', {
            'fields': ('tipo', 'telefono_destino', 'duracion_segundos', 'duracion_formateada')
        }),
        ('Contenido', {
            'fields': ('audio_url', 'transcripcion')
        }),
        ('Análisis', {
            'fields': (
                'analisis_sentimiento', 'palabras_clave_detectadas',
                'siguiente_accion_sugerida'
            )
        }),
        ('Resultado', {
            'fields': ('resultado',)
        }),
        ('API Externa', {
            'fields': ('call_sid', 'api_response'),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def resultado_badge(self, obj):
        colors = {
            'EXITOSA': '#28a745',
            'BUZON': '#ffc107',
            'NO_CONTESTA': '#dc3545',
            'RECHAZADA': '#dc3545',
            'NUMERO_INVALIDO': '#6c757d',
            'OCUPADO': '#ffc107'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.resultado, '#6c757d'),
            obj.get_resultado_display()
        )
    resultado_badge.short_description = 'Resultado'


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'lead', 'producto', 'agente', 'precio_final',
        'estado_badge', 'fue_venta_ia', 'fecha_venta'
    ]
    list_filter = ['estado', 'fue_venta_ia', 'agente', 'fecha_venta']
    search_fields = ['lead__nombre', 'lead__apellido', 'producto__nombre_plan']
    readonly_fields = ['created_at', 'updated_at', 'total_con_instalacion']
    date_hierarchy = 'fecha_venta'
    
    fieldsets = (
        ('Venta', {
            'fields': ('lead', 'producto')
        }),
        ('Agente', {
            'fields': ('agente', 'fue_venta_ia')
        }),
        ('Precios', {
            'fields': (
                'precio_final', 'descuento_aplicado', 'comision_agente',
                'total_con_instalacion'
            )
        }),
        ('Instalación', {
            'fields': ('fecha_venta', 'fecha_instalacion', 'direccion_instalacion')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        colors = {
            'PENDIENTE': '#ffc107',
            'INSTALADO': '#17a2b8',
            'ACTIVO': '#28a745',
            'SUSPENDIDO': '#6c757d',
            'CANCELADO': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.estado, '#6c757d'),
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
