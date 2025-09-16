from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import get_object_or_404
from . import views
from .payments import handle_stripe_webhook

urlpatterns = [
    # Páginas principales
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Clientes (CRUD)
    path('clientes/', views.ClientListView.as_view(), name='client_list'),
    path('clientes/agregar/', views.ClientCreateView.as_view(), name='client_create'),
    path('clientes/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clientes/<int:pk>/editar/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clientes/<int:pk>/eliminar/', views.ClientDeleteView.as_view(), name='client_delete'),
    
    # Servicios (CRUD)
    path('servicios/', views.ServiceListView.as_view(), name='service_list'),
    path('servicios/agregar/', views.ServiceCreateView.as_view(), name='service_create'),
    path('servicios/<int:pk>/editar/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('servicios/<int:pk>/eliminar/', views.ServiceDeleteView.as_view(), name='service_delete'),
    
    # Suscripciones (CRUD)
    path('suscripciones/', views.SubscriptionListView.as_view(), name='subscription_list'),
    path('suscripciones/agregar/<int:cliente_pk>/', views.SubscriptionCreateView.as_view(), name='subscription_create'),
    path('suscripciones/<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('suscripciones/<int:pk>/editar/', views.SubscriptionUpdateView.as_view(), name='subscription_update'),
    path('suscripciones/<int:pk>/eliminar/', views.SubscriptionDeleteView.as_view(), name='subscription_delete'),
    path('suscripciones/<int:pk>/cancelar/', views.subscription_cancel, name='subscription_cancel'),
    path('cancelar-suscripcion/<int:subscription_id>/', views.cancel_subscription, name='cancel_subscription'),
    
    # Pagos
    path('pagos/agregar/<int:subscription_id>/', views.add_payment, name='add_payment'),
    
    # Webhooks de Stripe
    path('webhook/stripe/', csrf_exempt(handle_stripe_webhook), name='stripe_webhook'),
    
    # Checkout y pagos
    path('checkout/<int:service_id>/', views.checkout, name='checkout'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    
    # Cron jobs para Railway
    path('cron/notifications/', views.cron_notifications, name='cron_notifications'),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
