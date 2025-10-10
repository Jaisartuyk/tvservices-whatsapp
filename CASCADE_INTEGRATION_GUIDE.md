# 🤖 GUÍA COMPLETA DE INTEGRACIÓN CASCADE CON PYTHONANYWHERE

## 📋 Resumen Ejecutivo

Esta guía te ayudará a conectar **Cascade** (tu asistente de IA) con tu aplicación Django en **PythonAnywhere**. La integración permite que Cascade pueda:

- 📊 Consultar datos de tu aplicación en tiempo real
- 🔄 Ejecutar comandos y operaciones
- 📱 Enviar notificaciones automáticas
- 📈 Generar reportes dinámicos
- 🔍 Monitorear el estado del sistema

---

## 🚀 CONFIGURACIÓN INICIAL

### 1. Archivos Creados

```
📁 Tu Proyecto/
├── 🤖 cascade_integration.py      # Sistema principal de integración
├── 🔗 cascade_urls.py            # URLs para las APIs
├── 📊 cascade_api_endpoints.py   # Endpoints específicos
└── 📋 CASCADE_INTEGRATION_GUIDE.md # Esta guía
```

### 2. Configurar URLs en Django

En tu archivo `urls.py` principal, agrega:

```python
from django.urls import path, include

urlpatterns = [
    # ... tus URLs existentes
    path('admin/', admin.site.urls),
    path('', include('control_utensilios.urls')),
    
    # 🤖 APIs para Cascade
    path('api/cascade/', include('cascade_urls')),
]
```

### 3. Configurar Variables de Entorno

En tu archivo `.env` o configuración de PythonAnywhere:

```bash
# 🔐 Credenciales para Cascade
CASCADE_API_KEY=tu_api_key_super_secreta_aqui
CASCADE_WEBHOOK_SECRET=tu_webhook_secret_aqui
CASCADE_WEBHOOK_URL=https://cascade-webhook-url.com/webhook

# 🌐 URL de tu app en PythonAnywhere
PYTHONANYWHERE_URL=https://tuusuario.pythonanywhere.com
```

---

## 🎯 OPCIONES DE CONEXIÓN

### Opción 1: 🤖 Webhooks (Recomendado)

**Cascade → Tu App**

```python
# URL del webhook en tu app
POST https://tuusuario.pythonanywhere.com/api/cascade/webhook/

# Headers
Authorization: Bearer tu_api_key_aqui
Content-Type: application/json

# Ejemplo de payload
{
    "command": "get_utensilios_data",
    "parameters": {
        "fecha": "2024-01-15",
        "modulo_id": 1
    }
}
```

### Opción 2: 📊 APIs REST

**Endpoints disponibles:**

```bash
# 📊 Obtener datos de utensilios
GET /api/cascade/utensilios/?fecha=2024-01-15&modulo_id=1

# 📈 Obtener datos del dashboard
GET /api/cascade/dashboard/?fecha=2024-01-15

# 📋 Crear reportes
POST /api/cascade/reports/
{
    "fecha": "2024-01-15",
    "tipo": "completo",
    "formato": "pdf"
}

# 🔍 Estado del sistema
GET /api/cascade/status/

# 💚 Health check
GET /api/cascade/health/

# 📱 Enviar notificaciones
POST /api/cascade/notify/
{
    "type": "alert",
    "message": "Stock bajo en módulo A",
    "recipients": ["+593999999999"],
    "channel": "whatsapp"
}
```

### Opción 3: 🔄 Cliente Python

**Tu App → Cascade**

```python
from cascade_integration import CascadeClient

# Inicializar cliente
client = CascadeClient(
    cascade_webhook_url="https://cascade-webhook-url.com/webhook",
    api_key="tu_api_key"
)

# Enviar notificación a Cascade
client.send_notification('data_update', {
    'table': 'control_diario',
    'operation': 'create',
    'data': {'modulo': 'A', 'cuchillos': 50}
})

# Enviar alerta del sistema
client.send_system_alert(
    'low_stock',
    'Stock de cuchillos bajo en módulo A',
    'warning'
)
```

---

## 🛠️ IMPLEMENTACIÓN PASO A PASO

### Paso 1: Subir Archivos a PythonAnywhere

1. **Sube los archivos** a tu directorio de proyecto en PythonAnywhere
2. **Actualiza las URLs** en tu `urls.py`
3. **Configura las variables** de entorno

### Paso 2: Configurar Autenticación

```python
# En cascade_integration.py, actualiza:
CASCADE_API_KEY = "tu_api_key_real_aqui"
WEBHOOK_SECRET = "tu_webhook_secret_real_aqui"
```

### Paso 3: Probar la Conexión

```bash
# Desde tu terminal local o Postman
curl -X GET \
  https://tuusuario.pythonanywhere.com/api/cascade/health/ \
  -H "Authorization: Bearer tu_api_key"

# Respuesta esperada:
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00",
    "version": "1.0.0"
}
```

### Paso 4: Configurar Cascade

En tu configuración de Cascade, agrega:

```json
{
    "integrations": {
        "pythonanywhere": {
            "base_url": "https://tuusuario.pythonanywhere.com/api/cascade/",
            "api_key": "tu_api_key",
            "endpoints": {
                "webhook": "webhook/",
                "utensilios": "utensilios/",
                "dashboard": "dashboard/",
                "status": "status/"
            }
        }
    }
}
```

---

## 📊 EJEMPLOS DE USO

### 1. Consultar Datos de Utensilios

```python
# Cascade puede ejecutar:
response = requests.get(
    "https://tuusuario.pythonanywhere.com/api/cascade/utensilios/",
    headers={"Authorization": "Bearer tu_api_key"},
    params={"fecha": "2024-01-15", "modulo_id": 1}
)

data = response.json()
print(f"Encontrados {len(data['data'])} registros")
```

### 2. Generar Reporte Automático

```python
# Cascade puede ejecutar:
response = requests.post(
    "https://tuusuario.pythonanywhere.com/api/cascade/reports/",
    headers={"Authorization": "Bearer tu_api_key"},
    json={
        "fecha": "2024-01-15",
        "tipo": "completo",
        "formato": "pdf",
        "modulo_id": 1
    }
)

reporte = response.json()
print(f"Reporte generado: {reporte['reporte']['file_path']}")
```

### 3. Monitorear Sistema

```python
# Cascade puede ejecutar:
response = requests.get(
    "https://tuusuario.pythonanywhere.com/api/cascade/status/",
    headers={"Authorization": "Bearer tu_api_key"}
)

status = response.json()
if status['system_status']['overall'] != 'OK':
    print("⚠️ Sistema con problemas!")
```

---

## 🔧 COMANDOS DJANGO PERSONALIZADOS

### Crear Comando de Sincronización

```bash
# En tu terminal de PythonAnywhere
python manage.py cascade_sync --action=sync_all

# Enviar reporte diario
python manage.py cascade_sync --action=send_report
```

### Automatizar con Cron

```bash
# En PythonAnywhere, configurar tarea programada:
# Todos los días a las 8:00 AM
0 8 * * * /home/tuusuario/.virtualenvs/tu_env/bin/python /home/tuusuario/mysite/manage.py cascade_sync --action=send_report
```

---

## 🚨 SEGURIDAD Y MEJORES PRÁCTICAS

### 1. Autenticación Robusta

```python
def validate_cascade_request(request):
    """🔐 Validación mejorada"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    
    # Validar token con timestamp para evitar replay attacks
    try:
        payload = jwt.decode(token, CASCADE_API_KEY, algorithms=['HS256'])
        return payload.get('exp', 0) > time.time()
    except jwt.InvalidTokenError:
        return False
```

### 2. Rate Limiting

```python
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests

def rate_limit_cascade(request):
    """⏱️ Limitar requests por minuto"""
    client_ip = request.META.get('REMOTE_ADDR')
    key = f"cascade_rate_limit_{client_ip}"
    
    requests_count = cache.get(key, 0)
    if requests_count >= 60:  # 60 requests por minuto
        return HttpResponseTooManyRequests("Rate limit exceeded")
    
    cache.set(key, requests_count + 1, 60)
    return None
```

### 3. Logging y Monitoreo

```python
import logging

logger = logging.getLogger('cascade_integration')

def log_cascade_activity(command, parameters, result, duration):
    """📝 Log detallado de actividad"""
    logger.info(f"Cascade Command: {command}")
    logger.info(f"Parameters: {parameters}")
    logger.info(f"Duration: {duration}ms")
    logger.info(f"Result: {result['status']}")
```

---

## 🔍 TROUBLESHOOTING

### Problemas Comunes

1. **Error 401 Unauthorized**
   - ✅ Verificar API key
   - ✅ Verificar header Authorization
   - ✅ Verificar formato: `Bearer tu_api_key`

2. **Error 500 Internal Server Error**
   - ✅ Revisar logs de Django
   - ✅ Verificar imports de modelos
   - ✅ Verificar conexión a base de datos

3. **Timeout en requests**
   - ✅ Verificar URL de PythonAnywhere
   - ✅ Verificar que la app esté activa
   - ✅ Verificar configuración de firewall

### Debug Mode

```python
# Activar debug en cascade_integration.py
DEBUG_CASCADE = True

if DEBUG_CASCADE:
    print(f"🔍 Debug: Command={command}, Params={parameters}")
    print(f"🔍 Debug: Result={result}")
```

---

## 📈 MÉTRICAS Y MONITOREO

### Dashboard de Métricas

```python
def get_cascade_metrics():
    """📊 Métricas de uso de Cascade"""
    from django.core.cache import cache
    
    return {
        'total_requests_today': cache.get('cascade_requests_today', 0),
        'successful_commands': cache.get('cascade_success_count', 0),
        'failed_commands': cache.get('cascade_error_count', 0),
        'average_response_time': cache.get('cascade_avg_response', 0),
        'most_used_commands': cache.get('cascade_popular_commands', [])
    }
```

---

## 🎯 PRÓXIMOS PASOS

1. **✅ Implementar** los archivos en tu proyecto
2. **🔧 Configurar** las credenciales y URLs
3. **🧪 Probar** la conexión con health check
4. **📊 Configurar** Cascade para usar las APIs
5. **🚀 Desplegar** y monitorear

---

## 📞 SOPORTE

Si necesitas ayuda con la implementación:

1. **Revisar logs** de Django en PythonAnywhere
2. **Probar endpoints** individualmente con Postman
3. **Verificar configuración** de URLs y credenciales
4. **Contactar soporte** si persisten los problemas

---

**🎉 ¡Listo! Ahora Cascade puede interactuar completamente con tu aplicación en PythonAnywhere.**
