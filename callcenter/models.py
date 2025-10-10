"""
Modelos para el Sistema de Call Center con IA
Gestión de leads, conversaciones, productos de telecomunicaciones y ventas
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Operador(models.Model):
    """Operadores de telecomunicaciones (Claro, Movistar, etc.)"""
    
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    logo = models.ImageField(upload_to='operadores/', blank=True, null=True, verbose_name='Logo')
    color_principal = models.CharField(max_length=7, default='#000000', help_text='Color en formato HEX')
    sitio_web = models.URLField(blank=True, null=True)
    telefono_atencion = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden de visualización')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Operador'
        verbose_name_plural = 'Operadores'
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class TipoServicio(models.TextChoices):
    """Tipos de servicios de telecomunicaciones"""
    INTERNET = 'INTERNET', 'Internet Hogar'
    MOVIL = 'MOVIL', 'Plan Móvil'
    TV = 'TV', 'TV por Cable'
    TELEFONIA = 'TELEFONIA', 'Telefonía Fija'
    COMBO = 'COMBO', 'Paquete Combo'


class Producto(models.Model):
    """Productos y planes de telecomunicaciones"""
    
    operador = models.ForeignKey(
        Operador, 
        on_delete=models.CASCADE, 
        related_name='productos',
        verbose_name='Operador'
    )
    tipo = models.CharField(
        max_length=20, 
        choices=TipoServicio.choices,
        verbose_name='Tipo de Servicio'
    )
    nombre_plan = models.CharField(max_length=200, verbose_name='Nombre del Plan')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    
    # Características específicas
    velocidad_mbps = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name='Velocidad (Mbps)',
        help_text='Para planes de Internet'
    )
    gigas_datos = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name='Gigas de Datos',
        help_text='Para planes móviles'
    )
    minutos_llamadas = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name='Minutos de Llamadas',
        help_text='Para planes móviles'
    )
    canales_tv = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name='Canales de TV',
        help_text='Para planes de TV'
    )
    
    # Precios
    precio_mensual = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Precio Mensual'
    )
    precio_instalacion = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        verbose_name='Precio de Instalación'
    )
    descuento_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Descuento (%)'
    )
    
    # Beneficios y restricciones
    beneficios = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Beneficios',
        help_text='Lista de beneficios del plan'
    )
    restricciones = models.TextField(
        blank=True,
        verbose_name='Restricciones',
        help_text='Letra pequeña, restricciones del plan'
    )
    
    # Disponibilidad
    zonas_disponibles = models.TextField(
        blank=True,
        verbose_name='Zonas Disponibles',
        help_text='Zonas geográficas donde está disponible'
    )
    
    # Control
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_destacado = models.BooleanField(default=False, verbose_name='Plan Destacado')
    stock_disponible = models.PositiveIntegerField(default=999, verbose_name='Stock Disponible')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-is_destacado', 'operador', 'tipo', 'precio_mensual']
        indexes = [
            models.Index(fields=['operador', 'tipo']),
            models.Index(fields=['is_active', 'is_destacado']),
        ]
    
    def __str__(self):
        return f"{self.operador.nombre} - {self.nombre_plan}"
    
    @property
    def precio_con_descuento(self):
        """Calcula el precio con descuento aplicado"""
        if self.descuento_porcentaje > 0:
            descuento = self.precio_mensual * (self.descuento_porcentaje / 100)
            return self.precio_mensual - descuento
        return self.precio_mensual
    
    @property
    def ahorro_mensual(self):
        """Calcula el ahorro mensual si hay descuento"""
        if self.descuento_porcentaje > 0:
            return self.precio_mensual * (self.descuento_porcentaje / 100)
        return Decimal('0.00')


class ClasificacionLead(models.TextChoices):
    """Clasificación de leads según temperatura"""
    HOT = 'HOT', '🔥 Hot Lead (Listo para comprar)'
    WARM = 'WARM', '🌡️ Warm Lead (Interesado)'
    COLD = 'COLD', '❄️ Cold Lead (Solo preguntando)'


class EstadoLead(models.TextChoices):
    """Estados del proceso de venta"""
    NUEVO = 'NUEVO', 'Nuevo'
    CONTACTADO = 'CONTACTADO', 'Contactado'
    CALIFICADO = 'CALIFICADO', 'Calificado'
    NEGOCIANDO = 'NEGOCIANDO', 'En Negociación'
    GANADO = 'GANADO', 'Venta Ganada'
    PERDIDO = 'PERDIDO', 'Venta Perdida'
    SEGUIMIENTO = 'SEGUIMIENTO', 'En Seguimiento'


class FuenteLead(models.TextChoices):
    """Fuente de origen del lead"""
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
    LLAMADA_ENTRANTE = 'LLAMADA_ENTRANTE', 'Llamada Entrante'
    LLAMADA_SALIENTE = 'LLAMADA_SALIENTE', 'Llamada Saliente'
    WEB = 'WEB', 'Formulario Web'
    REFERIDO = 'REFERIDO', 'Referido'
    REDES_SOCIALES = 'REDES_SOCIALES', 'Redes Sociales'
    OTRO = 'OTRO', 'Otro'


class Lead(models.Model):
    """Lead o cliente potencial"""
    
    # Información personal
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono', db_index=True)
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    direccion = models.TextField(blank=True, verbose_name='Dirección')
    zona = models.CharField(max_length=100, blank=True, verbose_name='Zona/Distrito')
    
    # Intereses
    operador_interes = models.ForeignKey(
        Operador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name='Operador de Interés'
    )
    producto_interes = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name='Producto de Interés'
    )
    tipo_servicio_interes = models.CharField(
        max_length=20,
        choices=TipoServicio.choices,
        blank=True,
        verbose_name='Tipo de Servicio de Interés'
    )
    presupuesto_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Presupuesto Estimado'
    )
    
    # Clasificación y scoring
    score = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Score (0-100)',
        help_text='Score de calidad del lead'
    )
    clasificacion = models.CharField(
        max_length=10,
        choices=ClasificacionLead.choices,
        default=ClasificacionLead.COLD,
        verbose_name='Clasificación'
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoLead.choices,
        default=EstadoLead.NUEVO,
        verbose_name='Estado'
    )
    fuente = models.CharField(
        max_length=30,
        choices=FuenteLead.choices,
        default=FuenteLead.WHATSAPP,
        verbose_name='Fuente'
    )
    
    # Asignación
    agente_asignado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads_asignados',
        verbose_name='Agente Asignado'
    )
    
    # Análisis de IA
    notas_ia = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Análisis de IA',
        help_text='Análisis automático generado por IA'
    )
    intenciones_detectadas = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Intenciones Detectadas',
        help_text='Intenciones detectadas en conversaciones'
    )
    objeciones = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Objeciones',
        help_text='Objeciones mencionadas por el lead'
    )
    
    # Seguimiento
    ultima_interaccion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Interacción'
    )
    proxima_accion = models.TextField(
        blank=True,
        verbose_name='Próxima Acción Sugerida'
    )
    fecha_proxima_accion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha Próxima Acción'
    )
    
    # Notas
    notas = models.TextField(blank=True, verbose_name='Notas Adicionales')
    
    # Control
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['telefono']),
            models.Index(fields=['clasificacion', 'estado']),
            models.Index(fields=['agente_asignado', 'estado']),
            models.Index(fields=['-score']),
        ]
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.get_clasificacion_display()}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del lead"""
        return f"{self.nombre} {self.apellido}".strip()
    
    def actualizar_score(self):
        """Calcula y actualiza el score del lead basado en interacciones"""
        score = 0
        
        # Puntos por tener producto de interés específico
        if self.producto_interes:
            score += 25
        
        # Puntos por presupuesto definido
        if self.presupuesto_estimado:
            score += 20
        
        # Puntos por número de conversaciones
        num_conversaciones = self.conversaciones.count()
        score += min(num_conversaciones * 10, 30)
        
        # Puntos por interacciones recientes (últimas 48 horas)
        if self.ultima_interaccion:
            horas_desde_ultima = (timezone.now() - self.ultima_interaccion).total_seconds() / 3600
            if horas_desde_ultima < 48:
                score += 25
        
        # Limitar score entre 0 y 100
        self.score = min(max(score, 0), 100)
        
        # Actualizar clasificación basada en score
        if self.score >= 80:
            self.clasificacion = ClasificacionLead.HOT
        elif self.score >= 50:
            self.clasificacion = ClasificacionLead.WARM
        else:
            self.clasificacion = ClasificacionLead.COLD
        
        self.save(update_fields=['score', 'clasificacion'])


class CanalConversacion(models.TextChoices):
    """Canales de comunicación"""
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
    LLAMADA = 'LLAMADA', 'Llamada Telefónica'
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    WEB_CHAT = 'WEB_CHAT', 'Chat Web'


class TipoConversacion(models.TextChoices):
    """Tipo de conversación"""
    ENTRANTE = 'ENTRANTE', 'Entrante'
    SALIENTE = 'SALIENTE', 'Saliente'


class SentimientoConversacion(models.TextChoices):
    """Sentimiento detectado en la conversación"""
    POSITIVO = 'POSITIVO', '😊 Positivo'
    NEUTRAL = 'NEUTRAL', '😐 Neutral'
    NEGATIVO = 'NEGATIVO', '😞 Negativo'


class Conversacion(models.Model):
    """Registro de conversaciones con leads"""
    
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='conversaciones',
        verbose_name='Lead'
    )
    canal = models.CharField(
        max_length=20,
        choices=CanalConversacion.choices,
        verbose_name='Canal'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoConversacion.choices,
        verbose_name='Tipo'
    )
    
    # Contenido
    mensaje_cliente = models.TextField(verbose_name='Mensaje del Cliente')
    respuesta_sistema = models.TextField(blank=True, verbose_name='Respuesta del Sistema')
    
    # Análisis
    transcripcion = models.TextField(
        blank=True,
        verbose_name='Transcripción',
        help_text='Transcripción completa de llamada'
    )
    duracion_segundos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Duración (segundos)'
    )
    sentimiento = models.CharField(
        max_length=20,
        choices=SentimientoConversacion.choices,
        default=SentimientoConversacion.NEUTRAL,
        verbose_name='Sentimiento'
    )
    
    # IA
    fue_atendido_por_ia = models.BooleanField(
        default=True,
        verbose_name='Atendido por IA'
    )
    agente_humano = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversaciones_atendidas',
        verbose_name='Agente Humano'
    )
    intenciones_detectadas = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Intenciones Detectadas'
    )
    objeciones_detectadas = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Objeciones Detectadas'
    )
    
    # Acción siguiente
    siguiente_accion = models.TextField(
        blank=True,
        verbose_name='Siguiente Acción Sugerida'
    )
    
    # Archivos
    audio_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL del Audio',
        help_text='Para llamadas grabadas'
    )
    
    # Control
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    
    class Meta:
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lead', '-created_at']),
            models.Index(fields=['canal', 'tipo']),
        ]
    
    def __str__(self):
        return f"{self.lead.nombre_completo} - {self.get_canal_display()} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"


class ResultadoLlamada(models.TextChoices):
    """Resultado de una llamada"""
    EXITOSA = 'EXITOSA', '✅ Exitosa'
    BUZON = 'BUZON', '📞 Buzón de Voz'
    NO_CONTESTA = 'NO_CONTESTA', '❌ No Contesta'
    RECHAZADA = 'RECHAZADA', '🚫 Rechazada'
    NUMERO_INVALIDO = 'NUMERO_INVALIDO', '⚠️ Número Inválido'
    OCUPADO = 'OCUPADO', '📵 Ocupado'


class LlamadaIA(models.Model):
    """Registro específico de llamadas realizadas por IA"""
    
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='llamadas',
        verbose_name='Lead'
    )
    conversacion = models.OneToOneField(
        Conversacion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='llamada_detalle',
        verbose_name='Conversación'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoConversacion.choices,
        verbose_name='Tipo'
    )
    telefono_destino = models.CharField(max_length=20, verbose_name='Teléfono Destino')
    
    # Detalles de la llamada
    duracion_segundos = models.PositiveIntegerField(default=0, verbose_name='Duración (segundos)')
    audio_url = models.URLField(blank=True, null=True, verbose_name='URL del Audio')
    transcripcion = models.TextField(blank=True, verbose_name='Transcripción')
    
    # Análisis
    analisis_sentimiento = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Análisis de Sentimiento'
    )
    palabras_clave_detectadas = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Palabras Clave Detectadas'
    )
    
    # Resultado
    resultado = models.CharField(
        max_length=20,
        choices=ResultadoLlamada.choices,
        default=ResultadoLlamada.NO_CONTESTA,
        verbose_name='Resultado'
    )
    siguiente_accion_sugerida = models.TextField(
        blank=True,
        verbose_name='Siguiente Acción Sugerida'
    )
    
    # API externa (Twilio, etc.)
    call_sid = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Call SID',
        help_text='ID de la llamada en Twilio'
    )
    api_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Respuesta de API'
    )
    
    # Control
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    
    class Meta:
        verbose_name = 'Llamada IA'
        verbose_name_plural = 'Llamadas IA'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lead', '-created_at']),
            models.Index(fields=['resultado']),
        ]
    
    def __str__(self):
        return f"Llamada a {self.lead.nombre_completo} - {self.get_resultado_display()}"
    
    @property
    def duracion_formateada(self):
        """Retorna la duración en formato MM:SS"""
        minutos = self.duracion_segundos // 60
        segundos = self.duracion_segundos % 60
        return f"{minutos:02d}:{segundos:02d}"


class EstadoVenta(models.TextChoices):
    """Estados de una venta"""
    PENDIENTE = 'PENDIENTE', 'Pendiente de Instalación'
    INSTALADO = 'INSTALADO', 'Instalado'
    ACTIVO = 'ACTIVO', 'Activo'
    SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
    CANCELADO = 'CANCELADO', 'Cancelado'


class Venta(models.Model):
    """Registro de ventas cerradas"""
    
    lead = models.ForeignKey(
        Lead,
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name='Lead/Cliente'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name='Producto'
    )
    
    # Agente responsable
    agente = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ventas_realizadas',
        verbose_name='Agente'
    )
    fue_venta_ia = models.BooleanField(
        default=False,
        verbose_name='Venta Cerrada por IA'
    )
    
    # Precios
    precio_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Final'
    )
    descuento_aplicado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Descuento Aplicado'
    )
    comision_agente = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Comisión del Agente'
    )
    
    # Instalación
    fecha_venta = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Venta')
    fecha_instalacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Instalación'
    )
    direccion_instalacion = models.TextField(verbose_name='Dirección de Instalación')
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=EstadoVenta.choices,
        default=EstadoVenta.PENDIENTE,
        verbose_name='Estado'
    )
    
    # Notas
    notas = models.TextField(blank=True, verbose_name='Notas')
    
    # Control
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lead', 'estado']),
            models.Index(fields=['agente', '-created_at']),
            models.Index(fields=['-fecha_venta']),
        ]
    
    def __str__(self):
        return f"Venta #{self.id} - {self.lead.nombre_completo} - {self.producto}"
    
    @property
    def total_con_instalacion(self):
        """Calcula el total incluyendo instalación"""
        return self.precio_final + self.producto.precio_instalacion
