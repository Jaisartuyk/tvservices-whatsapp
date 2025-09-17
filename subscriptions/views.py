import json
import logging
from datetime import date, datetime, timedelta
from django.db.models import Sum

import stripe
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Subscription, Service, Cliente, CategoriaServicio, Payment
from .forms import CustomUserCreationForm, SubscriptionForm, ServiceForm
from django.contrib.auth import get_user_model
from .payments import create_stripe_checkout_session, handle_stripe_webhook

# Importación diferida para evitar importación circular
ClientWithSubscriptionForm = None

def home(request):
    """Vista principal con información de servicios disponibles"""
    from django.db.models import Count, Q, Sum
    from datetime import date, timedelta
    
    # Si el usuario está autenticado, mostrar el dashboard
    if request.user.is_authenticated:
        
        # Obtener estadísticas para el dashboard
        total_clientes = Cliente.objects.filter(creado_por=request.user).count()
        
        # Obtener suscripciones activas
        suscripciones_activas = Subscription.objects.filter(
            cliente__creado_por=request.user,
            is_active=True
        ).count()
        
        # Obtener suscripciones que vencen en los próximos 7 días
        hoy = date.today()
        proxima_semana = hoy + timedelta(days=7)
        
        # Obtener el total mensual de suscripciones activas
        total_mensual = Subscription.objects.filter(
            cliente__creado_por=request.user,
            is_active=True
        ).aggregate(total=Sum('price'))['total'] or 0
        
        # Obtener las últimas 5 suscripciones
        ultimas_suscripciones = Subscription.objects.filter(
            cliente__creado_por=request.user
        ).select_related('cliente', 'service').order_by('-created_at')[:5]
        
        # Obtener suscripciones próximas a vencer (próximos 7 días)
        proximos_vencimientos = Subscription.objects.filter(
            cliente__creado_por=request.user,
            is_active=True,
            end_date__range=[hoy, proxima_semana]
        ).select_related('cliente', 'service').order_by('end_date')
        
        # Contar cuántas están por vencer
        proximas_a_vencer = proximos_vencimientos.count()
        
        # Crear listas con información adicional calculada
        ultimas_suscripciones_info = []
        if ultimas_suscripciones.exists():
            for sub in ultimas_suscripciones:
                # Verificación robusta de la suscripción
                if (sub and hasattr(sub, 'id') and sub.id and 
                    hasattr(sub, 'service') and sub.service and 
                    hasattr(sub, 'cliente') and sub.cliente and
                    hasattr(sub, 'end_date') and sub.end_date):
                    try:
                        ultimas_suscripciones_info.append({
                            'subscription': sub,
                            'dias_restantes': (sub.end_date - hoy).days,
                            'esta_activa': sub.is_active and sub.end_date >= hoy
                        })
                    except Exception as e:
                        # Si hay algún error, simplemente omitir esta suscripción
                        continue
            
        proximos_vencimientos_info = []
        if proximos_vencimientos.exists():
            for sub in proximos_vencimientos:
                # Verificación robusta de la suscripción
                if (sub and hasattr(sub, 'id') and sub.id and 
                    hasattr(sub, 'service') and sub.service and 
                    hasattr(sub, 'cliente') and sub.cliente and
                    hasattr(sub, 'end_date') and sub.end_date):
                    try:
                        proximos_vencimientos_info.append({
                            'subscription': sub,
                            'dias_restantes': (sub.end_date - hoy).days,
                            'esta_activa': sub.is_active and sub.end_date >= hoy
                        })
                    except Exception as e:
                        # Si hay algún error, simplemente omitir esta suscripción
                        continue
        
        context = {
            'total_clientes': total_clientes,
            'suscripciones_activas': suscripciones_activas,
            'proximas_a_vencer': proximas_a_vencer,
            'total_mensual': total_mensual,
            'ultimas_suscripciones': ultimas_suscripciones_info,
            'proximos_vencimientos': proximos_vencimientos_info,
            'hoy': hoy,
        }
    else:
        # Para usuarios no autenticados, mostrar información general
        services = Service.objects.filter(is_active=True).order_by('nombre_mostrar')
        categories = CategoriaServicio.objects.filter(is_active=True).prefetch_related('servicios')
        
        # Obtener estadísticas generales para mostrar a usuarios no autenticados
        total_servicios = services.count()
        total_usuarios = get_user_model().objects.count()
        
        context = {
            'services': services,
            'categories': categories,
            'total_servicios': total_servicios,
            'total_usuarios': total_usuarios,
            'hoy': date.today(),
        }
    
    return render(request, 'subscriptions/home.html', context)

def register(request):
    """Vista para registro de nuevos usuarios"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, '¡Cuenta creada exitosamente!')
                return redirect('home')
            except Exception as e:
                messages.error(request, 'Error al crear la cuenta. Intenta nuevamente.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

import logging
logger = logging.getLogger(__name__)

@login_required
def checkout(request, service_id=None):
    """Vista para procesar suscripciones"""
    logger.info(f"Iniciando checkout para service_id: {service_id}")
    
    # Si se accede a /checkout/ sin ID, redirigir a home
    if service_id is None:
        logger.warning("Acceso a checkout sin service_id")
        return redirect('home')
        
    # Obtener el servicio seleccionado
    try:
        service = Service.objects.get(id=service_id, is_active=True)
        logger.info(f"Servicio encontrado: {service.name} (ID: {service.id})")
    except Service.DoesNotExist:
        logger.error(f"Servicio no encontrado o inactivo: ID {service_id}")
        messages.error(request, 'El servicio seleccionado no está disponible.')
        return redirect('home')
    
    # Obtener los clientes del usuario actual
    clientes = Cliente.objects.filter(creado_por=request.user, is_active=True)
    
    if not clientes.exists():
        messages.warning(request, 'Debe registrar al menos un cliente antes de crear una suscripción.')
        return redirect('client_create')
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, user=request.user, service=service)
        
        if not form.is_valid():
            # Si el formulario no es válido, se mostrarán los errores en la plantilla
            pass
        else:
            try:
                # Iniciar transacción atómica
                with transaction.atomic():
                    # Crear la suscripción
                    subscription = form.save(commit=False)
                    subscription.service = service
                    subscription.save()
                    
                    # Procesar el pago
                    payment_method = form.cleaned_data.get('payment_method')
                    
                    if payment_method == 'card':
                        return _process_card_payment(request, service, subscription)
                    else:
                        return _process_manual_payment(request, subscription, payment_method)
            
            except Exception as e:
                logger.error(f'Error al procesar la suscripción: {str(e)}', exc_info=True)
                messages.error(request, 'Hubo un error al procesar su solicitud. Por favor, intente nuevamente.')
                return redirect('checkout', service_id=service.id)
    else:
        # Si solo hay un cliente, lo seleccionamos por defecto
        initial = {}
        if clientes.count() == 1:
            initial['cliente'] = clientes.first()
            
        form = SubscriptionForm(
            user=request.user, 
            service=service,
            initial=initial
        )
    
    context = {
        'service': service,
        'form': form,
        'clientes': clientes,
    }
    
    return render(request, 'subscriptions/checkout.html', context)

@login_required
def dashboard(request):
    # Obtener solo las suscripciones activas del usuario
    active_subscriptions = Subscription.objects.filter(
        cliente__creado_por=request.user,
        is_active=True,
        payment_status='paid'
    ).select_related('service').order_by('-created_at')
    
    # Obtener suscripciones inactivas o pendientes de pago
    inactive_subscriptions = Subscription.objects.filter(
        cliente__creado_por=request.user
    ).exclude(
        is_active=True,
        payment_status='paid'
    ).select_related('service').order_by('-created_at')
    
    # Calcular total mensual solo de suscripciones activas y pagadas
    total_monthly = sum(sub.price for sub in active_subscriptions if sub.is_active)
    
    context = {
        'active_subscriptions': active_subscriptions,
        'inactive_subscriptions': inactive_subscriptions,
        'total_monthly': total_monthly,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def cancel_subscription(request, subscription_id):
    """Vista para cancelar una suscripción"""
    subscription = get_object_or_404(Subscription, id=subscription_id, cliente__creado_por=request.user)
    
    if request.method == 'POST':
        subscription.is_active = False
        subscription.cancelled_at = timezone.now()
        subscription.save()
        messages.success(request, f'Has cancelado tu suscripción a {subscription.service.nombre_mostrar}.')
        return redirect('dashboard')
    
    return render(request, 'cancel_subscription.html', {
        'subscription': subscription
    })

def payment_success(request):
    """Vista para cuando el pago es exitoso"""
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.warning(request, 'No se pudo verificar el pago. Por favor, verifica en tu panel de control.')
        return redirect('dashboard')
    
    try:
        # Obtener detalles de la sesión de Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Verificar si el pago fue exitoso
        if session.payment_status == 'paid':
            messages.success(request, '¡Pago exitoso! Tu suscripción ha sido activada.')
            return redirect('dashboard')
        else:
            messages.warning(request, 'El pago no se ha completado correctamente. Por favor, verifica en tu panel de control.')
            return redirect('dashboard')
    except Exception as e:
        messages.error(request, 'Error al verificar el pago. Por favor, contacta al soporte.')
        return redirect('dashboard')

def payment_cancel(request):
    """Vista para cuando el usuario cancela el pago"""
    messages.warning(request, 'El pago fue cancelado.')
    return redirect('home')


def _process_card_payment(request, service, subscription):
    """Procesa el pago con tarjeta a través de Stripe"""
    try:
        logger.info("Iniciando proceso de pago con tarjeta")
        service_name = service.name.lower()
        logger.info(f"Buscando precio para servicio: {service_name}")
        
        # Buscar el precio en la configuración de Stripe
        price_id = None
        
        # Primero intenta con el nombre exacto (case insensitive)
        exact_match = next(
            (price for name, price in settings.STRIPE_PRICES.items() 
             if name.lower() == service_name.lower()),
            None
        )
        
        if exact_match:
            price_id = exact_match
            logger.info(f"Precio encontrado con coincidencia exacta: {price_id}")
        else:
            # Si no hay coincidencia exacta, intenta con variaciones
            variations = [
                service_name.replace('_', ' '),  # Reemplaza guiones bajos por espacios
                service_name.replace('_', ''),   # Elimina guiones bajos
                service_name.split('_')[0],      # Primera parte antes de guión bajo
                service_name.replace('_', '+'),  # Reemplaza guiones bajos por +
                service_name.replace('_', '')    # Sin guiones bajos
            ]
            
            for variation in set(variations):  # Usar set para eliminar duplicados
                if variation in settings.STRIPE_PRICES:
                    price_id = settings.STRIPE_PRICES[variation]
                    logger.info(f"Precio encontrado con variación '{variation}': {price_id}")
                    break
        
        if not price_id:
            error_msg = f'No se encontró un precio configurado para {service.name}.'
            logger.error(error_msg)
            messages.error(request, 'Error de configuración del servicio. Por favor, contacta al soporte.')
            return redirect('checkout', service_id=service.id)
        
        # Crear sesión de pago con Stripe
        checkout_session = create_stripe_checkout_session(
            request, 
            service, 
            price_id, 
            subscription
        )
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        logger.error(f'Error al crear sesión de pago con Stripe: {str(e)}', exc_info=True)
        messages.error(request, 'Error al procesar el pago con tarjeta. Por favor, intente nuevamente.')
        return redirect('checkout', service_id=service.id)


def _process_manual_payment(request, subscription, payment_method):
    """Procesa un pago manual (efectivo, transferencia, etc.)"""
    try:
        # Para pagos manuales (efectivo, transferencia, etc.)
        payment = Payment.objects.create(
            subscription=subscription,
            amount=subscription.price,
            payment_method=payment_method,
            payment_status='pending',
            payment_date=timezone.now(),
            created_by=request.user
        )
        
        # Actualizar el estado de la suscripción
        subscription.payment_status = 'pending'
        subscription.save()
        
        messages.success(
            request, 
            'Solicitud de suscripción recibida. Por favor, realiza el pago según las instrucciones.'
        )
        return redirect('dashboard')
        
    except Exception as e:
        logger.error(f'Error al procesar pago manual: {str(e)}', exc_info=True)
        messages.error(request, 'Error al procesar el pago. Por favor, intente nuevamente.')
        return redirect('checkout', service_id=subscription.service.id)

class SubscriptionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Vista para listar todas las suscripciones"""
    model = Subscription
    template_name = 'subscriptions/subscription_list.html'
    context_object_name = 'suscripciones'
    permission_required = 'subscriptions.view_subscription'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por cliente si se especifica
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        
        # Filtrar por estado
        estado = self.request.GET.get('estado')
        hoy = date.today()
        
        if estado == 'activas':
            queryset = queryset.filter(is_active=True, end_date__gte=hoy)
        elif estado == 'por_vencer':
            proxima_semana = hoy + timedelta(days=7)
            queryset = queryset.filter(
                is_active=True,
                end_date__range=[hoy, proxima_semana]
            )
        elif estado == 'vencidas':
            queryset = queryset.filter(is_active=True, end_date__lt=hoy)
        
        # Filtrar por búsqueda
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(cliente__nombres__icontains=search_query) |
                Q(cliente__apellidos__icontains=search_query) |
                Q(service__nombre_mostrar__icontains=search_query)
            )
        
        # Solo mostrar las suscripciones de los clientes del usuario actual
        if not self.request.user.is_superuser:
            queryset = queryset.filter(cliente__creado_por=self.request.user)
        
        return queryset.select_related('cliente', 'service').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoy = date.today()
        
        # Crear lista con información adicional calculada para suscripciones
        suscripciones_info = []
        for sub in context['suscripciones']:
            # Verificación robusta de la suscripción
            if (sub and hasattr(sub, 'id') and sub.id and 
                hasattr(sub, 'service') and sub.service and 
                hasattr(sub, 'cliente') and sub.cliente and
                hasattr(sub, 'end_date') and sub.end_date):
                try:
                    suscripciones_info.append({
                        'subscription': sub,
                        'dias_restantes': (sub.end_date - hoy).days,
                        'esta_activa': sub.is_active and sub.end_date >= hoy
                    })
                except Exception as e:
                    # Si hay algún error, simplemente omitir esta suscripción
                    continue
        
        # Reemplazar la lista original con la nueva estructura
        context['suscripciones'] = suscripciones_info
        
        # Obtener el cliente si se está filtrando por cliente
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            from .models import Cliente
            context['cliente'] = get_object_or_404(Cliente, id=cliente_id)
        
        # Agregar estadísticas al contexto
        if not self.request.user.is_superuser:
            queryset = self.get_queryset()
            context['total_suscripciones'] = queryset.count()
            context['suscripciones_activas'] = queryset.filter(
                is_active=True, 
                end_date__gte=hoy
            ).count()
            
            proxima_semana = hoy + timedelta(days=7)
            context['proximas_a_vencer'] = queryset.filter(
                is_active=True,
                end_date__range=[hoy, proxima_semana]
            ).count()
        
        return context


# Vistas para gestión de servicios
# ====================================

class ServiceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Vista para listar servicios"""
    model = Service
    template_name = 'subscriptions/service_list.html'
    context_object_name = 'servicios'
    permission_required = 'subscriptions.view_service'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro de búsqueda
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(nombre__icontains=search_query) |
                Q(nombre_mostrar__icontains=search_query) |
                Q(descripcion__icontains=search_query)
            )
            
        # Filtrar por categoría
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
            
        # Filtrar por estado
        estado = self.request.GET.get('estado')
        if estado == 'activos':
            queryset = queryset.filter(is_active=True)
        elif estado == 'inactivos':
            queryset = queryset.filter(is_active=False)
            
        return queryset.select_related('categoria').order_by('categoria__nombre', 'nombre_mostrar')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaServicio.objects.filter(is_active=True)
        context['total_servicios'] = self.get_queryset().count()
        context['servicios_activos'] = self.get_queryset().filter(is_active=True).count()
        return context


class ServiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Vista para crear un nuevo servicio"""
    model = Service
    form_class = ServiceForm
    template_name = 'subscriptions/service_form.html'
    permission_required = 'subscriptions.add_service'
    success_url = reverse_lazy('service_list')
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Servicio {self.object.nombre_mostrar} creado exitosamente.')
        return response


class ServiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Vista para actualizar un servicio existente"""
    model = Service
    form_class = ServiceForm
    template_name = 'subscriptions/service_form.html'
    permission_required = 'subscriptions.change_service'
    
    def get_success_url(self):
        return reverse_lazy('service_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Servicio {self.object.nombre_mostrar} actualizado exitosamente.')
        return response


class ServiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Vista para eliminar un servicio"""
    model = Service
    template_name = 'subscriptions/service_confirm_delete.html'
    permission_required = 'subscriptions.delete_service'
    success_url = reverse_lazy('service_list')
    
    def delete(self, request, *args, **kwargs):
        service = self.get_object()
        if service.tiene_suscripciones_activas():
            messages.error(request, 'No se puede eliminar un servicio con suscripciones activas.')
            return redirect('service_list')
            
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Servicio {service.nombre_mostrar} eliminado exitosamente.')
        return response


# Vistas para gestión de clientes
# ====================================

class ClientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cliente
    template_name = 'subscriptions/client_list.html'
    context_object_name = 'clientes'
    permission_required = 'subscriptions.view_cliente'
    paginate_by = 10
    
    def get_queryset(self):
        import logging
        logger = logging.getLogger(__name__)
        
        queryset = super().get_queryset()
        logger.info(f'Queryset inicial: {queryset.count()} clientes')
        
        # Filtro de búsqueda
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(nombres__icontains=search_query) |
                Q(apellidos__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(telefono__icontains=search_query)
            )
            logger.info(f'Después de búsqueda: {queryset.count()} clientes')
        
        # Si no es superusuario, mostrar solo los clientes que creó el usuario
        if not self.request.user.is_superuser:
            queryset = queryset.filter(creado_por=self.request.user)
            logger.info(f'Después de filtrar por creado_por: {queryset.count()} clientes')
        else:
            logger.info('Usuario es superusuario, mostrando todos los clientes')
            
        queryset = queryset.order_by('apellidos', 'nombres')
        logger.info(f'Query final: {queryset.query}')
        logger.info(f'Total de clientes a mostrar: {queryset.count()}')
        
        return queryset

class ClientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Cliente
    template_name = 'subscriptions/client_detail.html'
    context_object_name = 'cliente'
    permission_required = 'subscriptions.view_cliente'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(creado_por=self.request.user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()
        context['client'] = client  # Usar 'client' en lugar de 'cliente' para coincidir con la plantilla
        context['suscripciones'] = client.subscriptions.all().order_by('-start_date')
        context['suscripciones_activas'] = client.subscriptions.filter(is_active=True).count()
        context['suscripciones_vencidas'] = client.subscriptions.filter(
            is_active=True,
            end_date__lt=timezone.now().date()
        ).count()
        context['total_gastado'] = client.subscriptions.aggregate(
            total=Sum('price')
        )['total'] or 0
        return context

class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    template_name = 'subscriptions/client_form.html'
    permission_required = 'subscriptions.add_cliente'
    success_url = reverse_lazy('client_list')
    form_class = None  # Se establecerá en get_form_class
    
    def get_form_class(self):
        # Importación diferida para evitar importación circular
        from .forms import ClientWithSubscriptionForm
        return ClientWithSubscriptionForm
    
    def get_form_kwargs(self):
        """Pasa el usuario actual al formulario"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Agrega el título de la página al contexto"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Agregar Nuevo Cliente con Suscripción'
        return context
    
    def form_valid(self, form):
        # El formulario ya maneja la creación del cliente y la suscripción
        response = super().form_valid(form)
        
        # Mostrar mensaje de éxito
        messages.success(self.request, f'Cliente {self.object.nombres} {self.object.apellidos} ha sido creado exitosamente junto con su suscripción.')
        
        # Redirigir a la lista de clientes
        return response


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cliente
    fields = ['nombres', 'apellidos', 'email', 'telefono', 'direccion', 'fecha_nacimiento', 'notas', 'is_active']
    template_name = 'subscriptions/client_form.html'
    permission_required = 'subscriptions.change_cliente'
    success_url = reverse_lazy('client_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(creado_por=self.request.user)
        return queryset
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Configurar placeholders y clases CSS
        form.fields['nombres'].widget.attrs.update({'placeholder': 'Ingrese los nombres'})
        form.fields['apellidos'].widget.attrs.update({'placeholder': 'Ingrese los apellidos'})
        form.fields['email'].widget.attrs.update({'placeholder': 'correo@ejemplo.com'})
        form.fields['telefono'].widget.attrs.update({'placeholder': '+56912345678'})
        form.fields['direccion'].widget.attrs.update({'rows': 2})
        form.fields['notas'].widget.attrs.update({'rows': 3})
        return form
    
    def form_valid(self, form):
        # Actualizar la fecha de modificación
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'subscriptions/client_confirm_delete.html'
    permission_required = 'subscriptions.delete_cliente'
    success_url = reverse_lazy('client_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(creado_por=self.request.user)
        return queryset
    
    def delete(self, request, *args, **kwargs):
        # Verificar si el cliente tiene suscripciones activas
        self.object = self.get_object()
        if self.object.subscriptions.filter(is_active=True).exists():
            messages.error(
                request,
                'No se puede eliminar el cliente porque tiene suscripciones activas.'
            )
            return redirect('client_detail', pk=self.object.pk)
        
        # Registrar la eliminación
        messages.success(
            request,
            f'Cliente {self.object.nombre_completo} eliminado correctamente.'
        )
        return super().delete(request, *args, **kwargs)


# Vistas para suscripciones
class SubscriptionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Vista para mostrar los detalles de una suscripción"""
    model = Subscription
    template_name = 'subscriptions/subscription_detail.html'
    context_object_name = 'suscripcion'
    permission_required = 'subscriptions.view_subscription'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(cliente__creado_por=self.request.user)
        return queryset.select_related('cliente', 'service')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        suscripcion = self.get_object()
        hoy = date.today()
        
        # Calcular días restantes
        dias_restantes = (suscripcion.end_date - hoy).days
        
        # Obtener historial de pagos (si existe)
        pagos = suscripcion.payments.all().order_by('-payment_date')
        
        # Agregar datos al contexto
        context.update({
            'dias_restantes': dias_restantes,
            'esta_activa': suscripcion.is_active and suscripcion.end_date >= hoy,
            'pagos': pagos,
            'hoy': hoy,
        })
        
        return context


class SubscriptionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'subscriptions/subscription_form.html'
    permission_required = 'subscriptions.add_subscription'
    
    def get_success_url(self):
        return reverse('client_detail', kwargs={'pk': self.object.cliente.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = get_object_or_404(Cliente, pk=self.kwargs.get('cliente_pk'))
        context['cliente'] = cliente
        context['client'] = cliente  # Para compatibilidad con templates
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        cliente = get_object_or_404(Cliente, pk=self.kwargs.get('cliente_pk'))
        initial['cliente'] = cliente
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['cliente_id'] = self.kwargs.get('cliente_pk')
        return kwargs
    
    def form_valid(self, form):
        # Si es un nuevo registro, establecer fechas por defecto
        if not form.instance.pk:
            form.instance.start_date = timezone.now().date()
            form.instance.end_date = form.instance.start_date + timedelta(days=30)
        
        return super().form_valid(form)


class SubscriptionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'subscriptions/subscription_form.html'
    permission_required = 'subscriptions.change_subscription'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(cliente__creado_por=self.request.user)
        return queryset
    
    def get_success_url(self):
        return reverse('client_detail', kwargs={'pk': self.object.cliente.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.object.cliente
        context['cliente'] = cliente
        context['client'] = cliente  # Para compatibilidad con templates
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Registrar quién realizó la modificación
        form.instance.updated_by = self.request.user
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)


class SubscriptionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Subscription
    template_name = 'subscriptions/subscription_confirm_delete.html'
    permission_required = 'subscriptions.delete_subscription'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(cliente__creado_por=self.request.user)
        return queryset
    
    def get_success_url(self):
        return reverse('client_detail', kwargs={'pk': self.object.cliente.pk})
    
    def delete(self, request, *args, **kwargs):
        subscription = self.get_object()
        cliente_pk = subscription.cliente.pk
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Suscripción eliminada correctamente.')
        return redirect('client_detail', pk=cliente_pk)


@login_required
@permission_required('subscriptions.add_payment', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def add_payment(request, subscription_id):
    """
    Vista para agregar un pago a una suscripción
    """
    # Obtener la suscripción y verificar permisos
    subscription = get_object_or_404(
        Subscription.objects.select_related('cliente'), 
        pk=subscription_id
    )
    
    # Verificar que el usuario tenga permiso para ver esta suscripción
    if not request.user.is_superuser and subscription.cliente.creado_por != request.user:
        raise PermissionDenied("No tiene permiso para realizar esta acción.")
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Crear el pago
                    payment = form.save(commit=False)
                    payment.subscription = subscription
                    payment.created_by = request.user
                    payment.save()
                    
                    # Si el pago se marca como completado, actualizar la suscripción
                    if payment.payment_status == Payment.EstadoPago.COMPLETADO:
                        subscription.payment_status = 'paid'
                        subscription.payment_date = payment.payment_date
                        subscription.save()
                    
                    messages.success(request, 'Pago registrado correctamente.')
                    return redirect('subscription_detail', pk=subscription.pk)
                    
            except Exception as e:
                messages.error(request, f'Error al registrar el pago: {str(e)}')
    else:
        # Inicializar el formulario con valores por defecto
        initial = {
            'amount': subscription.price,
            'payment_date': timezone.now(),
            'payment_status': Payment.EstadoPago.COMPLETADO
        }
        form = PaymentForm(initial=initial)
    
    context = {
        'form': form,
        'subscription': subscription,
        'cliente': subscription.cliente,
        'title': 'Registrar Pago'
    }
    
    return render(request, 'subscriptions/payment_form.html', context)


@login_required
def subscription_cancel(request, pk):
    """
    Vista para cancelar una suscripción
    """
    subscription = get_object_or_404(Subscription, pk=pk)
    
    # Verificar permisos: solo el creador del cliente o superusuarios pueden cancelar
    if not request.user.is_superuser and subscription.cliente.creado_por != request.user:
        messages.error(request, 'No tienes permisos para cancelar esta suscripción.')
        return redirect('subscription_detail', pk=pk)
    
    if request.method == 'POST':
        if subscription.is_active:
            # Cancelar la suscripción usando el método del modelo
            reason = f"Cancelada por {request.user.get_full_name() or request.user.username} el {timezone.now().strftime('%d/%m/%Y %H:%M')}"
            subscription.cancel(reason=reason)
            
            messages.success(
                request, 
                f'La suscripción de {subscription.cliente.nombre_completo} '
                f'a {subscription.service.nombre_mostrar} ha sido cancelada exitosamente.'
            )
        else:
            messages.warning(request, 'Esta suscripción ya está cancelada.')
    
    return redirect('subscription_detail', pk=pk)


@csrf_exempt
def cron_notifications(request):
    """
    Endpoint para ejecutar notificaciones desde cron externo
    """
    if request.method == 'POST':
        try:
            import subprocess
            import sys
            
            # Ejecutar notificaciones para todos los días
            results = []
            
            for days in [0, 1, 3, 7]:
                try:
                    result = subprocess.run([
                        sys.executable, 'manage.py', 'send_expiration_notifications', 
                        '--days', str(days)
                    ], capture_output=True, text=True, timeout=300)
                    
                    results.append({
                        'days': days,
                        'success': result.returncode == 0,
                        'output': result.stdout,
                        'error': result.stderr
                    })
                    
                except Exception as e:
                    results.append({
                        'days': days,
                        'success': False,
                        'error': str(e)
                    })
            
            return JsonResponse({
                'success': True,
                'message': 'Notificaciones ejecutadas',
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido. Use POST.'
    })


@login_required
@require_POST
def send_manual_reminder(request, subscription_id):
    """
    Enviar recordatorio manual para una suscripción específica
    """
    try:
        # Obtener la suscripción
        subscription = get_object_or_404(
            Subscription.objects.select_related('cliente', 'service'),
            id=subscription_id,
            cliente__creado_por=request.user
        )
        
        # Importar el módulo services directamente
        from subscriptions import services as services_module
        
        # Calcular días restantes
        dias_restantes = subscription.dias_restantes
        
        # Crear instancia del servicio de notificaciones
        notification_service = services_module.NotificationService()
        
        # Enviar notificación usando el servicio existente
        resultado = notification_service.send_expiration_notification(
            subscription=subscription,
            days_until_expiration=dias_restantes
        )
        
        if resultado['success']:
            messages.success(
                request, 
                f'✅ Recordatorio enviado exitosamente a {subscription.cliente.nombre_completo}'
            )
            return JsonResponse({
                'success': True,
                'message': 'Recordatorio enviado exitosamente',
                'phone': subscription.cliente.telefono,
                'days_remaining': dias_restantes
            })
        else:
            messages.error(
                request, 
                f'❌ Error al enviar recordatorio: {resultado.get("error", "Error desconocido")}'
            )
            return JsonResponse({
                'success': False,
                'error': resultado.get('error', 'Error desconocido')
            })
            
    except Subscription.DoesNotExist:
        messages.error(request, '❌ Suscripción no encontrada')
        return JsonResponse({
            'success': False,
            'error': 'Suscripción no encontrada'
        })
    except Exception as e:
        logger.error(f"Error enviando recordatorio manual: {e}")
        messages.error(request, f'❌ Error inesperado: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
