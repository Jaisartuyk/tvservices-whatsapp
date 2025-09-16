# Sistema de Notificaciones de WhatsApp

Este documento explica cómo configurar y usar el sistema de notificaciones automáticas por WhatsApp para avisar a los clientes sobre el vencimiento de sus suscripciones.

## 🚀 Configuración Inicial

### 1. Obtener Credenciales de WaSender

1. Ve a [https://wasenderapi.com/](https://wasenderapi.com/)
2. Crea una cuenta y configura tu instancia de WhatsApp
3. Obtén las siguientes credenciales:
   - `API_KEY`: Tu clave de API
   - `INSTANCE_ID`: ID de tu instancia de WhatsApp

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
# Configuración de WaSender API
WASENDER_API_URL=https://wasenderapi.com/api
WASENDER_API_KEY=tu-api-key-aqui
WASENDER_INSTANCE_ID=tu-instance-id-aqui

# Configuración de notificaciones
ENABLE_WHATSAPP_NOTIFICATIONS=True
NOTIFICATION_TIME_HOUR=9
```

### 3. Aplicar Migraciones

```bash
python manage.py migrate
```

## 📱 Uso del Sistema

### Envío Manual de Notificaciones

Para enviar notificaciones manualmente, usa el comando de Django:

```bash
# Enviar notificaciones para suscripciones que vencen mañana (1 día)
python manage.py send_expiration_notifications --days 1

# Enviar notificaciones para suscripciones que vencen en 3 días
python manage.py send_expiration_notifications --days 3

# Modo de prueba (no envía mensajes reales)
python manage.py send_expiration_notifications --days 1 --dry-run

# Forzar envío aunque las notificaciones estén deshabilitadas
python manage.py send_expiration_notifications --days 1 --force
```

### Automatización con Cron (Linux/Mac) o Task Scheduler (Windows)

#### Linux/Mac - Crontab

Edita el crontab:
```bash
crontab -e
```

Agrega las siguientes líneas para enviar notificaciones diariamente a las 9 AM:

```bash
# Notificaciones 1 día antes del vencimiento
0 9 * * * cd /ruta/a/tu/proyecto && python manage.py send_expiration_notifications --days 1

# Notificaciones 3 días antes del vencimiento
0 9 * * * cd /ruta/a/tu/proyecto && python manage.py send_expiration_notifications --days 3

# Notificaciones 7 días antes del vencimiento
0 9 * * * cd /ruta/a/tu/proyecto && python manage.py send_expiration_notifications --days 7
```

#### Windows - Task Scheduler

1. Abre el Programador de tareas
2. Crea una nueva tarea básica
3. Configura para ejecutar diariamente a las 9:00 AM
4. Programa: `python.exe`
5. Argumentos: `manage.py send_expiration_notifications --days 1`
6. Directorio de inicio: `C:\ruta\a\tu\proyecto`

## 📊 Monitoreo y Logs

### Ver Registros de Notificaciones

El sistema registra todas las notificaciones en la base de datos. Puedes verlas en:

1. **Django Admin**: Ve a "Registros de Notificaciones"
2. **Logs de archivo**: Revisa `logs/notifications.log`

### Información Registrada

Para cada notificación se guarda:
- Cliente y suscripción
- Tipo de notificación
- Estado (Pendiente, Enviado, Fallido, Entregado)
- Número de teléfono
- Contenido del mensaje
- Fecha y hora de envío
- Respuesta de la API
- Errores (si los hay)

## 🎨 Personalización de Mensajes

### Modificar Plantillas de Mensajes

Los mensajes se generan en `subscriptions/services.py` en el método `_create_expiration_message()`.

Ejemplo de personalización:

```python
def _create_expiration_message(self, subscription, days_until_expiration: int) -> str:
    cliente_name = subscription.cliente.nombre_completo
    service_name = subscription.service.nombre_mostrar
    expiration_date = subscription.end_date.strftime('%d/%m/%Y')
    price = subscription.price
    
    # Tu mensaje personalizado aquí
    message = f"""
🔔 *¡Hola {cliente_name}!*

Tu suscripción a *{service_name}* vence en {days_until_expiration} día(s).

📅 Fecha de vencimiento: {expiration_date}
💰 Precio de renovación: ${price:,.0f}

¡Renueva ahora para seguir disfrutando!
    """.strip()
    
    return message
```

## 🛠️ Configuración Avanzada

### Configurar Múltiples Tipos de Notificaciones

En `settings.py` puedes configurar:

```python
NOTIFICATION_SETTINGS = {
    'EXPIRATION_DAYS_NOTICE': [1, 3, 7],  # Días antes del vencimiento
    'ENABLE_WHATSAPP_NOTIFICATIONS': True,
    'NOTIFICATION_TIME_HOUR': 9,  # Hora del día (9 AM)
}
```

### Agregar Nuevos Tipos de Notificación

1. Agrega el tipo en `NotificationLog.NotificationType`
2. Crea el método en `NotificationService`
3. Actualiza las plantillas de mensaje

## 🔍 Solución de Problemas

### Problemas Comunes

1. **"API key no configurada"**
   - Verifica que `WASENDER_API_KEY` esté en tu `.env`
   - Asegúrate de que la clave sea válida

2. **"Número de teléfono inválido"**
   - Los números deben incluir código de país
   - Formato: `573001234567` (sin + ni espacios)

3. **"No se envían notificaciones"**
   - Verifica que `ENABLE_WHATSAPP_NOTIFICATIONS=True`
   - Usa `--force` para forzar el envío

4. **"Error de conexión a la API"**
   - Verifica tu conexión a internet
   - Confirma que la URL de la API sea correcta

### Logs de Debug

Para ver más detalles, activa el logging de debug en `settings.py`:

```python
LOGGING = {
    'loggers': {
        'subscriptions.services': {
            'level': 'DEBUG',
        },
    },
}
```

## 📈 Métricas y Estadísticas

El sistema registra métricas útiles:

- Tasa de entrega de mensajes
- Errores por tipo
- Clientes sin teléfono registrado
- Horarios de mayor actividad

Puedes crear reportes personalizados consultando el modelo `NotificationLog`.

## 🔐 Seguridad

- Las credenciales de API se almacenan como variables de entorno
- Los logs no incluyen información sensible
- Los números de teléfono se validan antes del envío
- Se implementa rate limiting para evitar spam

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs en `logs/notifications.log`
2. Verifica la configuración en Django Admin
3. Consulta la documentación de WaSender API
4. Usa el modo `--dry-run` para probar sin enviar mensajes reales
