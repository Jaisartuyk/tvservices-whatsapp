# 🔧 Guía Técnica: Cómo Funciona el Sistema

## 🏗️ **Arquitectura del Sistema**

### **1. Aplicación Web (Railway)**
```
https://tvservices-whatsapp-production.up.railway.app
```
- **Django 4.2+** como framework principal
- **PostgreSQL** como base de datos
- **Gunicorn** como servidor web
- **Whitenoise** para archivos estáticos

### **2. Base de Datos**
```sql
-- Tablas principales
- Cliente: Información personal y contacto
- Service: Servicios disponibles (Netflix, HBO, etc.)
- Subscription: Suscripciones activas de cada cliente
- NotificationLog: Registro de todas las notificaciones enviadas
```

### **3. API de WhatsApp**
- **WaSender API** (https://wasenderapi.com/)
- **API Key**: Autenticación segura
- **Session ID**: Sesión de WhatsApp activa
- **Webhook**: Para recibir respuestas (opcional)

---

## ⚙️ **Flujo de Funcionamiento**

### **Paso 1: Registro de Cliente**
```python
# El cliente se registra con:
- Nombres y apellidos
- Teléfono (formato: +593968196046)
- Email
- Servicios que quiere (Netflix, HBO, etc.)
- Fechas de vencimiento
```

### **Paso 2: Almacenamiento**
```sql
-- Se guarda en la base de datos
INSERT INTO subscriptions_cliente (nombres, apellidos, telefono, email)
INSERT INTO subscriptions_subscription (cliente_id, service_id, end_date, price)
```

### **Paso 3: Cron Job Automático**
```bash
# Cada día a las 9 AM Ecuador (14:00 UTC)
0 14 * * * POST https://tu-app.railway.app/cron/notifications/
```

### **Paso 4: Procesamiento**
```python
# El sistema busca suscripciones que vencen en:
- 7 días (aviso temprano)
- 3 días (recordatorio)
- 1 día (último aviso)
- 0 días (vence hoy - urgente)
```

### **Paso 5: Envío de WhatsApp**
```python
# Para cada cliente que necesita aviso:
1. Genera mensaje personalizado
2. Llama a WaSender API
3. Envía el WhatsApp
4. Registra el envío en NotificationLog
```

---

## 📊 **Ejemplo de Ejecución Diaria**

### **9:00 AM - Cron se ejecuta:**
```
✅ Buscando suscripciones que vencen en 7 días...
   - Encontradas: 5 suscripciones
   - Enviados: 5 WhatsApp

✅ Buscando suscripciones que vencen en 3 días...
   - Encontradas: 3 suscripciones
   - Enviados: 3 WhatsApp

✅ Buscando suscripciones que vencen en 1 día...
   - Encontradas: 2 suscripciones
   - Enviados: 2 WhatsApp

🚨 Buscando suscripciones que vencen HOY...
   - Encontradas: 1 suscripción
   - Enviados: 1 WhatsApp URGENTE

📊 Total: 11 notificaciones enviadas
```

---

## 💬 **Estructura del Mensaje**

### **Plantilla del mensaje:**
```python
mensaje = f"""
🔔 Hola {cliente.nombre_completo}

Tu suscripción a {servicio.nombre} está por vencer:
📅 Vence: {fecha_vencimiento}
💰 Precio renovación: ${precio}
⏰ Quedan: {dias_restantes} días

Para renovar, responde este mensaje o contacta con nosotros.

¡Gracias por confiar en TV Services! 🎬
"""
```

### **Mensaje especial día 0:**
```python
mensaje_urgente = f"""
🚨 ¡URGENTE! Hola {cliente.nombre_completo}

Tu suscripción a {servicio.nombre} vence ¡HOY!
📅 Vence: Hoy, {fecha_vencimiento}
💰 Precio renovación: ${precio}

⚡ ¡Renueva AHORA para no perder el servicio!

Responde este mensaje inmediatamente.
"""
```

---

## 🔄 **Proceso de Envío WhatsApp**

### **1. Preparación del mensaje:**
```python
def enviar_notificacion(cliente, suscripcion, dias):
    # Limpiar número de teléfono
    telefono = limpiar_numero(cliente.telefono)
    
    # Generar mensaje personalizado
    mensaje = generar_mensaje(cliente, suscripcion, dias)
    
    # Enviar via WaSender API
    respuesta = wasender_api.enviar_mensaje(telefono, mensaje)
    
    # Registrar en base de datos
    NotificationLog.objects.create(
        cliente=cliente,
        subscription=suscripcion,
        message=mensaje,
        status='enviado' if respuesta.success else 'fallido'
    )
```

### **2. Llamada a WaSender API:**
```python
import requests

def enviar_whatsapp(telefono, mensaje):
    url = "https://wasenderapi.com/api/send"
    headers = {
        'Authorization': f'Bearer {WASENDER_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'session_id': WASENDER_SESSION_ID,
        'phone': telefono,
        'message': mensaje
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

---

## 📈 **Monitoreo y Logs**

### **1. Logs de Django:**
```python
# En Railway puedes ver logs de:
- Notificaciones enviadas
- Errores de API
- Suscripciones procesadas
- Estadísticas diarias
```

### **2. Base de datos:**
```sql
-- Consultar notificaciones enviadas hoy
SELECT * FROM subscriptions_notificationlog 
WHERE DATE(created_at) = CURRENT_DATE;

-- Ver estadísticas por día
SELECT 
    DATE(created_at) as fecha,
    COUNT(*) as total_enviados,
    SUM(CASE WHEN status = 'enviado' THEN 1 ELSE 0 END) as exitosos
FROM subscriptions_notificationlog 
GROUP BY DATE(created_at);
```

### **3. Cron-job.org Dashboard:**
```
- Historial de ejecuciones
- Status codes (200 = éxito)
- Tiempos de respuesta
- Errores si los hay
```

---

## 🛠️ **Mantenimiento**

### **Tareas regulares:**
1. **Verificar logs** en Railway
2. **Revisar estadísticas** de envío
3. **Actualizar información** de clientes
4. **Monitorear** WaSender API credits
5. **Backup** de base de datos

### **Solución de problemas:**
- **WhatsApp no llega**: Verificar número de teléfono
- **API error**: Revisar credits de WaSender
- **Cron no ejecuta**: Verificar cron-job.org
- **Base de datos**: Logs en Railway

---

## 🎯 **Ventajas del Sistema**

### **Para el negocio:**
- ✅ **Automatización completa** - Sin intervención manual
- ✅ **Escalable** - Maneja miles de clientes
- ✅ **Confiable** - Railway 99.9% uptime
- ✅ **Económico** - Costos bajos de operación

### **Para los clientes:**
- ✅ **Nunca olvidan renovar** - Avisos automáticos
- ✅ **Información clara** - Detalles completos
- ✅ **Múltiples avisos** - 4 oportunidades
- ✅ **Personalizado** - Mensajes con su nombre

---

## 📞 **URLs del Sistema**

```bash
# Aplicación principal
https://tvservices-whatsapp-production.up.railway.app/

# Panel de administración
https://tvservices-whatsapp-production.up.railway.app/admin/
Usuario: admin
Contraseña: admin123

# Dashboard de clientes
https://tvservices-whatsapp-production.up.railway.app/dashboard/

# Endpoint de cron (automático)
https://tvservices-whatsapp-production.up.railway.app/cron/notifications/
```

**¡Sistema completamente automatizado y funcionando 24/7!** 🚀
