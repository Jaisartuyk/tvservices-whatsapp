"""
URLs para el Call Center IA
"""
from django.urls import path
from . import views
from . import views_actions
from . import views_dashboards
from . import views_import
from . import views_update
from . import views_whatsapp
from . import views_test

app_name = 'callcenter'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # WhatsApp Detail (MOVED TO TOP)
    path('whatsapp/<int:conversacion_id>/', views_whatsapp.whatsapp_detail, name='whatsapp_detail'),
    path('whatsapp/<int:conversacion_id>/reply/', views_whatsapp.whatsapp_reply, name='whatsapp_reply'),
    
    # Leads
    path('leads/', views.leads_list, name='leads_list'),
    path('leads/<int:lead_id>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:lead_id>/update/', views_update.update_lead, name='update_lead'),
    path('leads/import/', views_import.import_leads, name='import_leads'),
    
    # Productos
    path('productos/', views.productos_list, name='productos_list'),
    
    # APIs para gráficos
    path('api/lead-stats/', views.api_lead_stats, name='api_lead_stats'),
    path('api/ventas-stats/', views.api_ventas_stats, name='api_ventas_stats'),
    # API para generar script de llamada (IA)
    path('api/generate-script/', views.api_generate_script, name='api_generate_script'),
    # APIs para dashboard en tiempo real
    path('api/recent-conversations/', views.api_recent_conversations, name='api_recent_conversations'),
    path('api/assign-conversation/', views.api_assign_conversation, name='api_assign_conversation'),
    # Dashboards específicos
    path('whatsapp-dashboard/', views_dashboards.whatsapp_dashboard, name='whatsapp_dashboard'),
    path('calls-dashboard/', views_dashboards.calls_dashboard, name='calls_dashboard'),
    
    # Test view
    path('test/', views_test.test_view, name='test_view'),
    path('test-whatsapp/<int:conversacion_id>/', views_test.test_whatsapp, name='test_whatsapp'),
    
    # WhatsApp Actions
    path('api/send-whatsapp/<int:lead_id>/', views_actions.api_send_whatsapp, name='api_send_whatsapp'),
    path('api/whatsapp-webhook/', views_actions.api_whatsapp_webhook, name='api_whatsapp_webhook'),
    
    # Call Actions
    path('api/make-call/<int:lead_id>/', views_actions.api_make_call, name='api_make_call'),
    path('api/call-webhook/', views_actions.api_call_webhook, name='api_call_webhook'),
    
    # Email Actions
    path('api/send-email/<int:lead_id>/', views_actions.api_send_email, name='api_send_email'),
]
