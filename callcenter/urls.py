"""
URLs para el Call Center IA
"""
from django.urls import path
from . import views

app_name = 'callcenter'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='home'),  # Alias para compatibilidad
    
    # Leads
    path('leads/', views.leads_list, name='leads_list'),
    path('leads/<int:lead_id>/', views.lead_detail, name='lead_detail'),
    
    # Productos
    path('productos/', views.productos_list, name='productos_list'),
    
    # APIs para gráficos
    path('api/lead-stats/', views.api_lead_stats, name='api_lead_stats'),
    path('api/ventas-stats/', views.api_ventas_stats, name='api_ventas_stats'),
]
