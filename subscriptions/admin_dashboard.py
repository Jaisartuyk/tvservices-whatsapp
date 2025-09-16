from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from django.db.models import Count, Sum, Q, F
from .models import Cliente, Service, Subscription, CategoriaServicio
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.utils.html import format_html

from .models import Service, Subscription, Cliente, CategoriaServicio

# ModelAdmins personalizados
class CategoriaServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'is_active', 'orden', 'servicio_count')
    list_filter = ('is_active',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('is_active', 'orden')
    ordering = ('orden', 'nombre')
    
    def servicio_count(self, obj):
        return obj.servicios.count()
    servicio_count.short_description = 'Servicios'
    servicio_count.admin_order_field = 'servicio_count'


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('nombre_mostrar', 'categoria', 'precio_base', 'tipo_suscripcion', 'is_active')
    list_filter = ('is_active', 'categoria', 'tipo_suscripcion', 'created_at')
    search_fields = ('nombre', 'nombre_mostrar', 'descripcion')
    list_editable = ('is_active', 'precio_base')
    ordering = ('categoria__nombre', 'nombre_mostrar')
    readonly_fields = ('created_at', 'updated_at', 'get_tipo_suscripcion_display')
    list_select_related = ('categoria',)
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'nombre_mostrar', 'descripcion', 'categoria')
        }),
        ('Precio y Suscripción', {
            'fields': ('precio_base', 'tipo_suscripcion', 'tipo_suscripcion_display')
        }),
        ('Estado y Metadatos', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
        ('Multimedia', {
            'fields': ('icono', 'imagen'),
            'classes': ('collapse',)
        }),
    )
    
    def precio_formateado(self, obj):
        return obj.precio_formateado
    precio_formateado.short_description = 'Precio'
    precio_formateado.admin_order_field = 'precio_base'
    
    def get_tipo_suscripcion_display(self, obj):
        return dict(Service.TipoSuscripcion.choices).get(obj.tipo_suscripcion, '')
    get_tipo_suscripcion_display.short_description = 'Tipo de Suscripción'


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'email', 'telefono', 'creado_por', 'suscripciones_count', 'is_active', 'fecha_registro')
    list_filter = ('is_active', 'fecha_registro', 'creado_por')
    search_fields = ('nombres', 'apellidos', 'email', 'telefono')
    list_editable = ('is_active',)
    readonly_fields = ('fecha_registro', 'fecha_actualizacion', 'suscripciones_count')
    date_hierarchy = 'fecha_registro'
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'email')
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'direccion', 'fecha_nacimiento')
        }),
        ('Información Adicional', {
            'fields': ('notas', 'is_active')
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si no es superusuario, solo mostrar los clientes que creó el usuario
        if not request.user.is_superuser:
            qs = qs.filter(creado_por=request.user)
        return qs
    
    def save_model(self, request, obj, form, change):
        # Asignar el usuario actual como creador si es un nuevo cliente
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
    
    def suscripciones_count(self, obj):
        return obj.subscriptions.count()
    suscripciones_count.short_description = 'Suscripciones'
    suscripciones_count.admin_order_field = 'subscriptions__count'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'servicio_nombre', 'price', 'payment_status', 'is_active', 'start_date', 'end_date', 'dias_restantes')
    list_filter = ('payment_status', 'is_active', 'payment_method', 'service', 'start_date')
    search_fields = ('cliente__nombres', 'cliente__apellidos', 'cliente__email', 
                    'service__nombre', 'service__nombre_mostrar')
    list_editable = ('payment_status', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'dias_restantes')
    date_hierarchy = 'created_at'
    list_select_related = ('cliente', 'service')
    
    fieldsets = (
        ('Información de la Suscripción', {
            'fields': ('cliente', 'service', 'price')
        }),
        ('Estado y Pagos', {
            'fields': ('payment_status', 'payment_method', 'payment_reference', 'is_active')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'payment_date', 'dias_restantes')
        }),
        ('Stripe', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id', 'stripe_payment_intent'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si no es superusuario, solo mostrar las suscripciones de los clientes que creó el usuario
        if not request.user.is_superuser:
            qs = qs.filter(cliente__creado_por=request.user)
        return qs
    
    def cliente_nombre(self, obj):
        return obj.cliente.nombre_completo
    cliente_nombre.short_description = 'Cliente'
    cliente_nombre.admin_order_field = 'cliente__apellidos'
    
    def servicio_nombre(self, obj):
        return obj.service.nombre_mostrar
    servicio_nombre.short_description = 'Servicio'
    servicio_nombre.admin_order_field = 'service__nombre_mostrar'
    
    def dias_restantes(self, obj):
        return obj.dias_restantes
    dias_restantes.short_description = 'Días restantes'
    
    def save_model(self, request, obj, form, change):
        # Lógica adicional al guardar la suscripción
        super().save_model(request, obj, form, change)
    
    def save_model(self, request, obj, form, change):
        # Lógica adicional al guardar el modelo desde el admin
        if not obj.pk:  # Si es una nueva suscripción
            obj.created_by = request.user
        obj.updated_by = request.user

        # Si se cancela la suscripción, establecer la fecha de cancelación
        if 'is_active' in form.changed_data and not obj.is_active:
            obj.cancelled_at = timezone.now()
            
        super().save_model(request, obj, form, change)

# UserAdmin personalizado
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'get_subscription_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    list_per_page = 20
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_subscription_count(self, obj):
        # Versión segura que verifica si el atributo existe
        if hasattr(obj, 'subscriptions'):
            return obj.subscriptions.count()
        return 0
    get_subscription_count.short_description = 'Suscripciones'
    get_subscription_count.admin_order_field = 'subscriptions__count'

# Decorador para verificar superusuario
def superuser_required(view_func):
    def _wrapped_view(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            from django.contrib.auth.views import redirect_to_login
            from django.urls import reverse
            return redirect_to_login(
                request.get_full_path(),
                reverse('admin:login')
            )
        return view_func(self, request, *args, **kwargs)
    return _wrapped_view

# ============================================
# Configuración del Panel de Administración Personalizado
# ============================================
class CustomAdminSite(admin.AdminSite):
    site_header = 'Panel de Control - TV Services'
    site_title = 'Administración TV Services'
    index_title = 'Resumen del Sistema'
    
    def has_permission(self, request):
        """
        Usuarios activos con permisos de administrador pueden acceder a este panel
        """
        return request.user.is_active and (request.user.is_superuser or request.user.is_staff)
    
    def get_urls(self):
        """
        Agrega las URLs personalizadas al admin.
        """
        from django.urls import path
        urls = super().get_urls()
        
        # Crear una vista envuelta con admin_view
        def index_wrapper(request, extra_context=None):
            return self.index(request, extra_context)
            
        # Obtener la vista del índice con el wrapper
        index_view = self.admin_view(index_wrapper)
        
        # Configurar las URLs personalizadas
        custom_urls = [
            path('', index_view, name='index'),
        ]
        
        return custom_urls + urls
    
    @superuser_required
    def index(self, request, extra_context=None):
        """
        Muestra la página de inicio del panel de administración.
        """
        # Obtener el contexto base
        context = {}
        
        # Solo cargar estadísticas si el usuario es superusuario
        if request.user.is_superuser:
            # Obtener estadísticas
            stats_data = self.get_system_stats()
            
            # Agregar al contexto
            context.update({
                'stats': stats_data['stats'],
                'latest_users': User.objects.order_by('-date_joined')[:5],
                'latest_subscriptions': stats_data['recent_subscriptions'],
                'popular_services': stats_data['popular_services'],
                'subscription_labels': stats_data['subscription_labels'],
                'subscription_data': stats_data['subscription_data'],
                'revenue_labels': stats_data['revenue_labels'],
                'revenue_data': stats_data['revenue_data'],
            })
        
        # Obtener el menú de la aplicación
        app_list = self.get_app_list(request)
        
        # Actualizar el contexto con la configuración del sitio
        context.update({
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            'available_apps': app_list,  # Para compatibilidad
            'site_title': self.site_title,
            'site_header': self.site_header,
            'index_title': self.index_title,
            'has_permission': self.has_permission(request),
            **(extra_context or {}),
        })
        
        # Depuración: imprimir claves del contexto
        print("\n=== CONTEXTO ENVIADO A LA PLANTILLA ===")
        print("Claves del contexto:", sorted(context.keys()))
        if 'stats' in context:
            print("Estadísticas:", context['stats'])
        if 'latest_subscriptions' in context:
            print("Suscripciones recientes:", [f"{sub.user.username} - {sub.service.name}" for sub in context['latest_subscriptions']])
        
        # Usar la plantilla personalizada
        return TemplateResponse(request, 'admin/dashboard.html', context)
    
    def get_system_stats(self):
        """ Obtener estadísticas del sistema """
        from django.db.models.functions import TruncMonth
        
        print("\n=== INICIANDO OBTENCIÓN DE ESTADÍSTICAS ===")
        
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=365)
        
        # Verificar si hay datos en las tablas
        print(f"Total de usuarios: {User.objects.count()}")
        print(f"Total de suscripciones: {Subscription.objects.count()}")
        print(f"Total de servicios: {Service.objects.count()}")
        
        # Estadísticas de suscripciones por mes
        subscription_data = list(
            Subscription.objects
            .filter(created_at__range=(start_date, end_date))
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )
        print(f"Datos de suscripciones por mes: {subscription_data}")
        
        # Estadísticas de ingresos por mes
        revenue_data = list(
            Subscription.objects
            .filter(created_at__range=(start_date, end_date))
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('price'))
            .order_by('month')
        )
        print(f"Datos de ingresos por mes: {revenue_data}")
        
        # Estadísticas generales
        stats = {
            'total_users': User.objects.count(),
            'active_subscriptions': Subscription.objects.filter(is_active=True).count(),
            'monthly_revenue': Subscription.objects.filter(
                created_at__month=timezone.now().month,
                created_at__year=timezone.now().year
            ).aggregate(Sum('price'))['price__sum'] or 0,
            'new_users': User.objects.filter(
                date_joined__month=timezone.now().month,
                date_joined__year=timezone.now().year
            ).count(),
        }
        
        print(f"Estadísticas generales: {stats}")
        
        # Obtener servicios populares
        popular_services = list(Service.objects.annotate(
            sub_count=Count('subscriptions')
        ).order_by('-sub_count')[:5])
        print(f"Servicios populares: {[(s.nombre, s.sub_count) for s in popular_services]}")
        
        # Obtener últimas suscripciones
        recent_subscriptions = list(Subscription.objects.select_related(
            'user', 'service'
        ).order_by('-created_at')[:10])
        print(f"Últimas suscripciones: {[(s.user.username, s.service.nombre) for s in recent_subscriptions]})")
        
        result = {
            'subscription_labels': [item['month'].strftime('%b') for item in subscription_data],
            'subscription_data': [item['total'] for item in subscription_data],
            'revenue_labels': [item['month'].strftime('%b') for item in revenue_data],
            'revenue_data': [float(item['total'] or 0) for item in revenue_data],
            'stats': stats,
            'popular_services': popular_services,
            'recent_subscriptions': recent_subscriptions
        }
        
        print("\n=== RESULTADO FINAL ===")
        print(f"Total de etiquetas de suscripción: {len(result['subscription_labels'])}")
        print(f"Total de datos de suscripción: {len(result['subscription_data'])}")
        print(f"Total de servicios populares: {len(result['popular_services'])}")
        print(f"Total de suscripciones recientes: {len(result['recent_subscriptions'])}")
        
        return result

# Crear instancia del admin personalizado
admin_site = CustomAdminSite(name='custom_admin')

# Registrar modelos en el admin personalizado
admin_site.register(User, CustomUserAdmin)
admin_site.register(Group, admin.ModelAdmin)
admin_site.register(Permission, admin.ModelAdmin)

# Registrar modelos de la aplicación
admin_site.register(CategoriaServicio, CategoriaServicioAdmin)
admin_site.register(Service, ServiceAdmin)
admin_site.register(Cliente, ClienteAdmin)
admin_site.register(Subscription, SubscriptionAdmin)

# Configurar títulos del sitio
admin_site.site_header = 'Administración de TV Services'
admin_site.site_title = 'TV Services Admin'
admin_site.index_title = 'Panel de Control'