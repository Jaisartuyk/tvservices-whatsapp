"""
URLs para el Call Center IA
"""
from django.urls import path
from . import views

app_name = 'callcenter'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Leads
    path('leads/', views.leads_list, name='leads_list'),
    path('leads/<int:lead_id>/', views.lead_detail, name='lead_detail'),
    
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
    path('whatsapp-dashboard/', views.whatsapp_dashboard, name='whatsapp_dashboard'),
    path('calls-dashboard/', views.calls_dashboard, name='calls_dashboard'),
    
    # WhatsApp Actions
    path('api/send-whatsapp/<int:lead_id>/', views.api_send_whatsapp, name='api_send_whatsapp'),
    path('api/whatsapp-webhook/', views.api_whatsapp_webhook, name='api_whatsapp_webhook'),
    
    # Call Actions
    path('api/make-call/<int:lead_id>/', views.api_make_call, name='api_make_call'),
    path('api/call-webhook/', views.api_call_webhook, name='api_call_webhook'),
    
    # Email Actions
    path('api/send-email/<int:lead_id>/', views.api_send_email, name='api_send_email'),
]
