# 🚨 Notificaciones Día 0 - TV Services

## 📋 ¿Qué son las Notificaciones Día 0?

Las **notificaciones día 0** son alertas que se envían automáticamente por WhatsApp **el mismo día que vence una suscripción**. Estas notificaciones son críticas porque:

- ⚠️ **Última oportunidad**: Es el último día para renovar antes de perder el servicio
- 🚨 **Máxima urgencia**: Requieren acción inmediata del cliente
- 📱 **Contacto directo**: Permiten respuesta inmediata del cliente

## 🎯 Configuración Actual

### Días de Notificación Configurados:
```python
EXPIRATION_DAYS_NOTICE = [0, 1, 3, 7]
```

- **7 días antes**: Aviso temprano 📅
- **3 días antes**: Recordatorio intermedio ⏰  
- **1 día antes**: Alerta de proximidad ⚠️
- **0 días (HOY)**: Notificación crítica 🚨

## 💬 Mensaje Día 0

El mensaje para día 0 tiene características especiales:

```
🚨 *TV Services - Recordatorio de Vencimiento*

Hola *Cliente Nombre*,

Te recordamos que tu suscripción a *Netflix Premium* vence ¡HOY!

📋 *Detalles:*
• Servicio: Netflix Premium
• Fecha de vencimiento: 15/09/2025
• Valor de renovación: $15,990

💡 *Para renovar tu suscripción:*
1. Contacta con nosotros
2. Realiza el pago correspondiente
3. ¡Sigue disfrutando sin interrupciones!

📞 ¿Necesitas ayuda? Responde a este mensaje.

*TV Services* - Tu entretenimiento sin límites
```

### Características del Mensaje Día 0:
- 🚨 **Emoji de emergencia**: Indica máxima urgencia
- ⚠️ **Texto "¡HOY!"**: Enfatiza la inmediatez
- 📞 **Call-to-action directo**: Invita a responder inmediatamente

## 🚀 Uso y Comandos

### Envío Manual Día 0:
```bash
# Solo notificaciones que vencen HOY
python manage.py send_expiration_notifications --days 0

# Modo de prueba (sin envío real)
python manage.py send_expiration_notifications --days 0 --dry-run

# Forzar envío (ignorar configuración global)
python manage.py send_expiration_notifications --days 0 --force
```

### Automatización Completa:
```bash
# Configuración cron recomendada (4 comandos diarios a las 9 AM)
0 9 * * * cd /proyecto && python manage.py send_expiration_notifications --days 0
0 9 * * * cd /proyecto && python manage.py send_expiration_notifications --days 1  
0 9 * * * cd /proyecto && python manage.py send_expiration_notifications --days 3
0 9 * * * cd /proyecto && python manage.py send_expiration_notifications --days 7
```

### Windows Task Scheduler:
1. **Crear 4 tareas separadas** (una por cada día)
2. **Día 0**: `python manage.py send_expiration_notifications --days 0`
3. **Programar**: Diariamente a las 9:00 AM
4. **Directorio**: Ruta del proyecto

## 🧪 Pruebas

### Script de Prueba Específico:
```bash
# Prueba completa del sistema día 0
python test_notificacion_dia_0.py
```

### Crear Suscripción de Prueba:
```python
# En Django shell
from datetime import date
from subscriptions.models import Subscription

# Cambiar fecha de vencimiento a HOY
subscription = Subscription.objects.get(id=1)
subscription.end_date = date.today()
subscription.save()
```

## 📊 Monitoreo Día 0

### Django Admin:
- Ve a **"Registros de Notificaciones"**
- Filtra por **"Tipo: Aviso de vencimiento"**
- Busca mensajes que contengan **"¡HOY!"**

### Consultas Útiles:
```python
# Notificaciones día 0 enviadas hoy
from subscriptions.models import NotificationLog
from datetime import date

day_0_today = NotificationLog.objects.filter(
    created_at__date=date.today(),
    message__icontains='¡HOY!'
)

print(f"Notificaciones día 0 hoy: {day_0_today.count()}")
```

### Logs:
```bash
# Ver logs de notificaciones
tail -f logs/notifications.log | grep "día 0\|HOY"
```

## 📈 Estadísticas y Métricas

### KPIs Importantes:
- **Tasa de respuesta día 0**: % de clientes que responden
- **Tasa de renovación día 0**: % de clientes que renuevan el mismo día
- **Tiempo de respuesta**: Cuánto tardan en responder

### Consulta de Renovaciones Día 0:
```python
# Suscripciones renovadas el mismo día de vencimiento
same_day_renewals = Subscription.objects.filter(
    end_date=F('updated_at__date'),
    payment_status='paid'
)
```

## 🎯 Mejores Prácticas

### 1. **Horario Óptimo**:
- **9:00 AM**: Hora de mayor actividad
- **Evitar fines de semana**: Menor respuesta
- **Considerar zona horaria**: Ecuador (UTC-5)

### 2. **Seguimiento**:
- Monitorear respuestas en WhatsApp
- Tener personal disponible para atender consultas
- Preparar respuestas rápidas para renovaciones

### 3. **Personalización**:
- Usar nombre completo del cliente
- Incluir detalles específicos del servicio
- Ofrecer múltiples formas de contacto

## 🔧 Solución de Problemas

### Problema: No se envían notificaciones día 0
```bash
# Verificar suscripciones que vencen hoy
python manage.py shell
>>> from subscriptions.models import Subscription
>>> from datetime import date
>>> today_expirations = Subscription.objects.filter(end_date=date.today(), is_active=True)
>>> print(f"Suscripciones que vencen hoy: {today_expirations.count()}")
```

### Problema: Mensaje no llega
```bash
# Verificar configuración
python manage.py test_whatsapp_service --phone +593968196046
```

### Problema: Error en comando
```bash
# Ejecutar con debug
python manage.py send_expiration_notifications --days 0 --dry-run
```

## 📞 Soporte

### Contacto de Emergencia:
- **WhatsApp**: +593 968 196 046
- **Email**: soporte@tvservices.com
- **Horario**: 24/7 para notificaciones día 0

### Escalación:
1. **Nivel 1**: Verificar logs y configuración
2. **Nivel 2**: Revisar API de WaSender
3. **Nivel 3**: Contactar soporte técnico

---

**🚨 Recuerda: Las notificaciones día 0 son críticas para la retención de clientes. Monitorea constantemente su funcionamiento.**
