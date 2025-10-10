# 🤖 INTEGRACIÓN CASCADE CON PYTHONANYWHERE
# Sistema completo para conectar Cascade con tu aplicación

import requests
import json
import logging
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import hashlib
import hmac

# 📊 CONFIGURACIÓN
PYTHONANYWHERE_BASE_URL = "https://tuusuario.pythonanywhere.com"  # Cambiar por tu URL
CASCADE_API_KEY = "tu_api_key_aqui"  # Para autenticación
WEBHOOK_SECRET = "tu_webhook_secret_aqui"  # Para validar webhooks

# 🔧 CONFIGURAR LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# 🎯 OPCIÓN 1: API REST ENDPOINTS PARA CASCADE
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def cascade_webhook(request):
    """
    🤖 Webhook principal para recibir comandos de Cascade
    URL: /api/cascade/webhook/
    """
    try:
        # Validar autenticación
        if not validate_cascade_request(request):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        # Procesar datos
        data = json.loads(request.body)
        command = data.get('command')
        parameters = data.get('parameters', {})
        
        logger.info(f"🤖 Cascade command received: {command}")
        
        # Ejecutar comando
        result = execute_cascade_command(command, parameters)
        
        return JsonResponse({
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error in cascade webhook: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

def validate_cascade_request(request):
    """🔐 Validar que la request viene de Cascade"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    return token == CASCADE_API_KEY

def execute_cascade_command(command, parameters):
    """⚡ Ejecutar comandos específicos de Cascade"""
    commands = {
        'get_utensilios_data': get_utensilios_data,
        'create_report': create_report,
        'update_stock': update_stock,
        'get_dashboard_data': get_dashboard_data,
        'execute_query': execute_custom_query,
        'send_notification': send_whatsapp_notification,
        'backup_data': backup_database,
        'get_system_status': get_system_status
    }
    
    if command in commands:
        return commands[command](parameters)
    else:
        raise ValueError(f"Unknown command: {command}")

# =============================================================================
# 🎯 OPCIÓN 2: FUNCIONES ESPECÍFICAS PARA CADA OPERACIÓN
# =============================================================================

def get_utensilios_data(parameters):
    """📊 Obtener datos de utensilios"""
    from control_utensilios.models import StockUtensilio, ControlDiario
    
    fecha = parameters.get('fecha', datetime.now().date())
    modulo_id = parameters.get('modulo_id')
    
    # Consultar datos
    queryset = ControlDiario.objects.filter(fecha=fecha)
    if modulo_id:
        queryset = queryset.filter(modulo_id=modulo_id)
    
    data = []
    for control in queryset:
        data.append({
            'id': control.id,
            'fecha': control.fecha.isoformat(),
            'modulo': control.modulo.nombre,
            'entregados': {
                'cuchillos': control.cuchillos_entregados,
                'crochet': control.crochet_entregados,
                'tijeras': control.tijeras_entregadas
            },
            'devueltos': {
                'cuchillos': control.cuchillos_devueltos,
                'crochet': control.crochet_devueltos,
                'tijeras': control.tijeras_devueltas
            }
        })
    
    return {
        'total_records': len(data),
        'data': data,
        'fecha_consulta': fecha.isoformat()
    }

def create_report(parameters):
    """📋 Crear reporte automático"""
    from control_utensilios.utils import generar_reporte_pdf
    
    fecha = parameters.get('fecha', datetime.now().date())
    modulo_id = parameters.get('modulo_id')
    tipo_reporte = parameters.get('tipo', 'completo')
    
    # Generar reporte
    reporte_path = generar_reporte_pdf(fecha, modulo_id, tipo_reporte)
    
    return {
        'reporte_generado': True,
        'path': reporte_path,
        'fecha': fecha.isoformat(),
        'tipo': tipo_reporte
    }

def update_stock(parameters):
    """📦 Actualizar stock de utensilios"""
    from control_utensilios.models import StockUtensilio
    
    modulo_id = parameters.get('modulo_id')
    updates = parameters.get('updates', {})
    
    try:
        stock = StockUtensilio.objects.get(modulo_id=modulo_id)
        
        # Actualizar campos
        for field, value in updates.items():
            if hasattr(stock, field):
                setattr(stock, field, value)
        
        stock.save()
        
        return {
            'updated': True,
            'modulo_id': modulo_id,
            'changes': updates
        }
        
    except StockUtensilio.DoesNotExist:
        return {'error': 'Stock no encontrado'}

def get_dashboard_data(parameters):
    """📈 Obtener datos para dashboard"""
    from control_utensilios.views import dashboard_view
    from django.test import RequestFactory
    
    # Simular request
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    
    # Obtener datos del dashboard
    response = dashboard_view(request)
    
    return {
        'dashboard_ready': True,
        'timestamp': datetime.now().isoformat()
    }

def execute_custom_query(parameters):
    """🔍 Ejecutar consulta personalizada"""
    from django.db import connection
    
    query = parameters.get('query')
    if not query:
        return {'error': 'No query provided'}
    
    # Validar query (solo SELECT permitido)
    if not query.strip().upper().startswith('SELECT'):
        return {'error': 'Only SELECT queries allowed'}
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            
            data = []
            for row in results:
                data.append(dict(zip(columns, row)))
        
        return {
            'query_executed': True,
            'columns': columns,
            'data': data,
            'row_count': len(data)
        }
        
    except Exception as e:
        return {'error': f'Query error: {str(e)}'}

def send_whatsapp_notification(parameters):
    """📱 Enviar notificación WhatsApp"""
    message = parameters.get('message')
    phone = parameters.get('phone')
    
    # Aquí integrarías con tu sistema de WhatsApp
    # Por ejemplo, usando la API de WhatsApp Business
    
    return {
        'notification_sent': True,
        'phone': phone,
        'message': message[:50] + '...' if len(message) > 50 else message
    }

def backup_database(parameters):
    """💾 Crear backup de la base de datos"""
    import subprocess
    from django.conf import settings
    
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    # Comando para backup (ajustar según tu configuración)
    cmd = f"mysqldump -u {settings.DATABASES['default']['USER']} -p{settings.DATABASES['default']['PASSWORD']} {settings.DATABASES['default']['NAME']} > {backup_name}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        return {
            'backup_created': True,
            'filename': backup_name,
            'timestamp': datetime.now().isoformat()
        }
    except subprocess.CalledProcessError as e:
        return {'error': f'Backup failed: {str(e)}'}

def get_system_status(parameters):
    """🔍 Obtener estado del sistema"""
    from django.db import connection
    import psutil
    import os
    
    # Estado de la base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "OK"
    except:
        db_status = "ERROR"
    
    # Estado del sistema
    system_info = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'python_version': os.sys.version,
        'database_status': db_status
    }
    
    return {
        'system_status': 'OK',
        'details': system_info,
        'timestamp': datetime.now().isoformat()
    }

# =============================================================================
# 🎯 OPCIÓN 3: CLIENTE PARA ENVIAR DATOS A CASCADE
# =============================================================================

class CascadeClient:
    """🤖 Cliente para enviar datos a Cascade"""
    
    def __init__(self, cascade_webhook_url, api_key):
        self.webhook_url = cascade_webhook_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def send_notification(self, event_type, data):
        """📤 Enviar notificación a Cascade"""
        payload = {
            'event': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'source': 'pythonanywhere_app'
        }
        
        try:
            response = self.session.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"✅ Notification sent to Cascade: {event_type}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to send notification to Cascade: {str(e)}")
            return None
    
    def send_data_update(self, table_name, operation, record_data):
        """📊 Enviar actualización de datos"""
        return self.send_notification('data_update', {
            'table': table_name,
            'operation': operation,  # 'create', 'update', 'delete'
            'data': record_data
        })
    
    def send_system_alert(self, alert_type, message, severity='info'):
        """🚨 Enviar alerta del sistema"""
        return self.send_notification('system_alert', {
            'type': alert_type,
            'message': message,
            'severity': severity
        })

# =============================================================================
# 🎯 OPCIÓN 4: MIDDLEWARE PARA MONITOREO AUTOMÁTICO
# =============================================================================

class CascadeMonitoringMiddleware:
    """🔍 Middleware para monitorear automáticamente la app"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cascade_client = CascadeClient(
            cascade_webhook_url="https://cascade-webhook-url.com/webhook",
            api_key=CASCADE_API_KEY
        )
    
    def __call__(self, request):
        # Antes de la vista
        start_time = datetime.now()
        
        response = self.get_response(request)
        
        # Después de la vista
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Enviar métricas a Cascade si es necesario
        if duration > 5:  # Si la request toma más de 5 segundos
            self.cascade_client.send_system_alert(
                'slow_request',
                f'Slow request detected: {request.path} took {duration:.2f}s',
                'warning'
            )
        
        return response

# =============================================================================
# 🎯 OPCIÓN 5: COMANDOS DE DJANGO PARA INTEGRACIÓN
# =============================================================================

# Crear archivo: management/commands/cascade_sync.py
DJANGO_COMMAND_CODE = '''
from django.core.management.base import BaseCommand
from cascade_integration import CascadeClient
import json

class Command(BaseCommand):
    help = 'Sincronizar datos con Cascade'
    
    def add_arguments(self, parser):
        parser.add_argument('--action', type=str, help='Acción a ejecutar')
        parser.add_argument('--data', type=str, help='Datos en formato JSON')
    
    def handle(self, *args, **options):
        client = CascadeClient(
            cascade_webhook_url="https://cascade-webhook-url.com/webhook",
            api_key="tu_api_key"
        )
        
        action = options['action']
        data = json.loads(options['data']) if options['data'] else {}
        
        if action == 'sync_all':
            self.sync_all_data(client)
        elif action == 'send_report':
            self.send_daily_report(client)
        
        self.stdout.write(
            self.style.SUCCESS(f'Cascade sync completed: {action}')
        )
    
    def sync_all_data(self, client):
        # Sincronizar todos los datos
        from control_utensilios.models import StockUtensilio
        
        stocks = StockUtensilio.objects.all()
        for stock in stocks:
            client.send_data_update('stock_utensilio', 'sync', {
                'id': stock.id,
                'modulo': stock.modulo.nombre,
                'cuchillos': stock.cuchillos_disponibles,
                'crochet': stock.crochet_disponibles,
                'tijeras': stock.tijeras_disponibles
            })
    
    def send_daily_report(self, client):
        # Enviar reporte diario
        from datetime import date
        from control_utensilios.models import ControlDiario
        
        today = date.today()
        controles = ControlDiario.objects.filter(fecha=today)
        
        report_data = {
            'fecha': today.isoformat(),
            'total_controles': controles.count(),
            'resumen': 'Reporte diario generado automáticamente'
        }
        
        client.send_notification('daily_report', report_data)
'''

# =============================================================================
# 🎯 URLS PARA LAS APIS
# =============================================================================

URLS_CODE = '''
# Agregar a urls.py
from django.urls import path
from . import cascade_integration

urlpatterns = [
    # ... tus URLs existentes
    
    # APIs para Cascade
    path('api/cascade/webhook/', cascade_integration.cascade_webhook, name='cascade_webhook'),
    path('api/cascade/status/', cascade_integration.get_system_status, name='cascade_status'),
]
'''

if __name__ == "__main__":
    print("🤖 Cascade Integration System")
    print("=" * 50)
    print("✅ Sistema de integración creado exitosamente")
    print("📋 Próximos pasos:")
    print("1. Configurar las URLs en tu proyecto Django")
    print("2. Actualizar las credenciales y URLs")
    print("3. Probar la conexión con Cascade")
    print("4. Implementar el monitoreo automático")
