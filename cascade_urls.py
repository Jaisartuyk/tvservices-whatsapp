# 🔗 URLs PARA INTEGRACIÓN CON CASCADE
# Agregar estas URLs a tu archivo urls.py principal

from django.urls import path, include
from . import cascade_integration

# URLs específicas para Cascade
cascade_urlpatterns = [
    # 🤖 Webhook principal para recibir comandos de Cascade
    path('webhook/', cascade_integration.cascade_webhook, name='cascade_webhook'),
    
    # 📊 Endpoints específicos para datos
    path('utensilios/', cascade_integration.api_get_utensilios, name='cascade_utensilios'),
    path('dashboard/', cascade_integration.api_get_dashboard, name='cascade_dashboard'),
    path('reports/', cascade_integration.api_create_report, name='cascade_reports'),
    
    # 🔍 Endpoints de sistema
    path('status/', cascade_integration.api_system_status, name='cascade_status'),
    path('health/', cascade_integration.api_health_check, name='cascade_health'),
    
    # 📱 Endpoints de notificaciones
    path('notify/', cascade_integration.api_send_notification, name='cascade_notify'),
]

# En tu urls.py principal, agregar:
urlpatterns = [
    # ... tus URLs existentes
    path('admin/', admin.site.urls),
    path('', include('control_utensilios.urls')),
    
    # 🤖 APIs para Cascade
    path('api/cascade/', include(cascade_urlpatterns)),
]
