# 📱 Sistema de Notificaciones WhatsApp - TV Services

## 🚀 Configuración Rápida

### 1. Ejecutar Script de Configuración Automática

```bash
python setup_notifications.py
```

Este script automáticamente:
- ✅ Verifica requisitos
- ✅ Crea archivo `.env`
- ✅ Ejecuta migraciones
- ✅ Crea directorio de logs
- ✅ Prueba la configuración

### 2. Configurar Credenciales de WaSender

1. Ve a [https://wasenderapi.com/](https://wasenderapi.com/)
2. Crea una cuenta gratuita
3. Configura tu instancia de WhatsApp
4. Obtén tus credenciales:
   - `API_KEY`
   - `INSTANCE_ID`

5. Edita el archivo `.env`:
```bash
WASENDER_API_KEY=tu-api-key-aqui
WASENDER_INSTANCE_ID=tu-instance-id-aqui
```

## 🧪 Pruebas del Sistema

### Probar Configuración
```bash
python manage.py test_whatsapp_service
```

### Probar con Número Real
```bash
python manage.py test_whatsapp_service --phone 573001234567
```

### Probar Notificaciones (Sin Envío Real)
```bash
python manage.py send_expiration_notifications --days 1 --dry-run
```

## 📅 Uso en Producción

### Envío Manual
```bash
# Notificar suscripciones que vencen mañana
python manage.py send_expiration_notifications --days 1

# Notificar suscripciones que vencen en 3 días
python manage.py send_expiration_notifications --days 3
```

### Automatización con Cron (Linux/Mac)
```bash
# Editar crontab
crontab -e

# Agregar líneas para envío automático diario a las 9 AM
0 9 * * * cd /ruta/a/tu/proyecto && python manage.py send_expiration_notifications --days 1
0 9 * * * cd /ruta/a/tu/proyecto && python manage.py send_expiration_notifications --days 3
0 9 * * * cd /ruta/a/tu/proyecto && python manage.py send_expiration_notifications --days 7
```

### Automatización con Task Scheduler (Windows)
1. Abre "Programador de tareas"
2. Crear tarea básica
3. Nombre: "Notificaciones WhatsApp TV Services"
4. Desencadenador: Diariamente a las 9:00 AM
5. Acción: Iniciar programa
   - Programa: `python.exe`
   - Argumentos: `manage.py send_expiration_notifications --days 1`
   - Directorio: `C:\ruta\a\tu\proyecto`

## 📊 Monitoreo

### Django Admin
- Ve a "Registros de Notificaciones"
- Filtra por estado, tipo, fecha
- Ve detalles de cada envío

### Logs de Archivo
```bash
# Ver logs en tiempo real
tail -f logs/notifications.log

# Ver últimas 50 líneas
tail -50 logs/notifications.log
```

## 🎨 Personalización

### Modificar Mensajes
Edita `subscriptions/services.py` en el método `_create_expiration_message()`:

```python
def _create_expiration_message(self, subscription, days_until_expiration: int) -> str:
    # Tu mensaje personalizado aquí
    message = f"""
🔔 ¡Hola {subscription.cliente.nombre_completo}!

Tu suscripción a {subscription.service.nombre_mostrar} vence en {days_until_expiration} día(s).

¡Renueva ahora para seguir disfrutando!
    """.strip()
    
    return message
```

### Configurar Días de Aviso
En `settings.py`:

```python
NOTIFICATION_SETTINGS = {
    'EXPIRATION_DAYS_NOTICE': [1, 3, 7, 15],  # Personaliza los días
    'ENABLE_WHATSAPP_NOTIFICATIONS': True,
    'NOTIFICATION_TIME_HOUR': 9,  # Hora preferida
}
```

## 🔧 Solución de Problemas

### Error: "API key no configurada"
```bash
# Verificar variables de entorno
python manage.py test_whatsapp_service
```

### Error: "Número de teléfono inválido"
- Formato correcto: `573001234567` (sin + ni espacios)
- Incluir código de país (57 para Colombia)

### No se envían notificaciones
```bash
# Forzar envío
python manage.py send_expiration_notifications --days 1 --force

# Verificar configuración
python manage.py test_whatsapp_service
```

### Ver logs detallados
```bash
# Activar debug en settings.py
LOGGING = {
    'loggers': {
        'subscriptions.services': {
            'level': 'DEBUG',
        },
    },
}
```

## 📈 Estadísticas Útiles

### Consultas en Django Shell
```python
from subscriptions.models import NotificationLog

# Notificaciones del último mes
NotificationLog.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=30)
).count()

# Tasa de éxito
total = NotificationLog.objects.count()
exitosas = NotificationLog.objects.filter(status='sent').count()
tasa_exito = (exitosas / total) * 100 if total > 0 else 0

# Errores más comunes
NotificationLog.objects.filter(
    status='failed'
).values('error_message').annotate(
    count=Count('id')
).order_by('-count')
```

## 🔐 Seguridad

- ✅ Credenciales en variables de entorno
- ✅ Validación de números de teléfono
- ✅ Rate limiting automático
- ✅ Logs sin información sensible
- ✅ Permisos de admin restringidos

## 🆘 Soporte

### Recursos Útiles
- 📚 [Documentación WaSender](https://wasenderapi.com/docs)
- 🐛 [Issues del Proyecto](https://github.com/tu-repo/issues)
- 💬 [Comunidad Django](https://forum.djangoproject.com/)

### Contacto
- 📧 Email: soporte@tvservices.com
- 💬 WhatsApp: +57 300 123 4567
- 🌐 Web: https://tvservices.com

---

**¡Listo para automatizar tus notificaciones! 🚀**
