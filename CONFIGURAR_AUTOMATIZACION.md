# 🤖 Configurar Automatización de Notificaciones WhatsApp

## ⏰ HORARIOS AUTOMÁTICOS CONFIGURADOS

### 📅 Programación Diaria:
- **9:00 AM**: Envío de todas las notificaciones
- **Zona horaria**: Ecuador (UTC-5)
- **Días**: Todos los días del año

### 📱 Tipos de Notificación:
- **Día 0**: Vence HOY 🚨 (crítico)
- **Día 1**: Vence mañana ⚠️ (urgente)
- **Día 3**: Vence en 3 días ⏰ (importante)
- **Día 7**: Vence en 7 días 📅 (aviso)

---

## 🪟 CONFIGURACIÓN EN WINDOWS (Task Scheduler)

### Paso 1: Abrir Programador de Tareas
1. Presiona `Win + R`
2. Escribe `taskschd.msc`
3. Presiona Enter

### Paso 2: Crear Tarea para Día 0 (Crítico)
1. **Clic derecho** en "Biblioteca del Programador de tareas"
2. **Seleccionar** "Crear tarea básica..."
3. **Configurar**:
   - **Nombre**: `WhatsApp Notificaciones Día 0`
   - **Descripción**: `Envío automático de notificaciones críticas (vence hoy)`

### Paso 3: Configurar Desencadenador
1. **Seleccionar**: "Diariamente"
2. **Hora de inicio**: `09:00:00`
3. **Repetir cada**: `1 días`

### Paso 4: Configurar Acción
1. **Seleccionar**: "Iniciar un programa"
2. **Programa**: `C:\Users\H P\Downloads\tvservices_project\venv\Scripts\python.exe`
3. **Argumentos**: `manage.py send_expiration_notifications --days 0`
4. **Iniciar en**: `C:\Users\H P\Downloads\tvservices_project`

### Paso 5: Repetir para Otros Días
Crear 3 tareas más con los mismos pasos pero cambiando:

**Tarea 2: Día 1**
- **Nombre**: `WhatsApp Notificaciones Día 1`
- **Argumentos**: `manage.py send_expiration_notifications --days 1`

**Tarea 3: Día 3**
- **Nombre**: `WhatsApp Notificaciones Día 3`
- **Argumentos**: `manage.py send_expiration_notifications --days 3`

**Tarea 4: Día 7**
- **Nombre**: `WhatsApp Notificaciones Día 7`
- **Argumentos**: `manage.py send_expiration_notifications --days 7`

---

## 🐧 CONFIGURACIÓN EN LINUX/MAC (Cron)

### Editar Crontab:
```bash
crontab -e
```

### Agregar estas líneas:
```bash
# Notificaciones WhatsApp diarias a las 9:00 AM
0 9 * * * cd /ruta/completa/proyecto && python manage.py send_expiration_notifications --days 0
0 9 * * * cd /ruta/completa/proyecto && python manage.py send_expiration_notifications --days 1
0 9 * * * cd /ruta/completa/proyecto && python manage.py send_expiration_notifications --days 3
0 9 * * * cd /ruta/completa/proyecto && python manage.py send_expiration_notifications --days 7
```

---

## 🐍 CONFIGURACIÓN CON SCRIPT PYTHON (Alternativa)

### Usar el script automático:
```bash
# Ejecutar en segundo plano
python auto_notifications.py
```

### Características del script:
- ✅ **9:00 AM**: Todas las notificaciones
- ✅ **6:00 PM**: Solo día 0 (urgentes)
- ✅ **Ejecución continua**: Se mantiene corriendo
- ✅ **Rate limiting**: 5 segundos entre envíos

---

## 📊 VERIFICACIÓN DE FUNCIONAMIENTO

### Comando de Prueba:
```bash
# Probar envío inmediato
python manage.py send_expiration_notifications --days 0 --dry-run
```

### Logs a Revisar:
```bash
# Ver logs de notificaciones
type logs\notifications.log
```

### Django Admin:
- Ve a **"Registros de Notificaciones"**
- Verifica envíos diarios a las 9:00 AM

---

## ⚡ CONFIGURACIÓN RÁPIDA (5 MINUTOS)

### Para Windows:
1. **Abrir**: `Win + R` → `taskschd.msc`
2. **Crear**: 4 tareas (días 0, 1, 3, 7)
3. **Programar**: Diariamente 9:00 AM
4. **Comando**: `python manage.py send_expiration_notifications --days X`

### Para verificar que funciona:
1. **Crear tarea de prueba** para dentro de 2 minutos
2. **Verificar** que se ejecute correctamente
3. **Ajustar** horario a 9:00 AM

---

## 🚨 IMPORTANTE

### Requisitos:
- ✅ **Computadora encendida** a las 9:00 AM
- ✅ **Internet activo** para WaSender API
- ✅ **Proyecto funcionando** sin errores
- ✅ **Variables de entorno** configuradas

### Monitoreo:
- **Django Admin**: Revisar registros diarios
- **Logs**: Verificar envíos exitosos
- **WhatsApp**: Confirmar recepción de mensajes

---

## 📞 SOPORTE

Si tienes problemas:
1. **Verificar** que el comando manual funciona
2. **Revisar** logs de errores
3. **Probar** con tarea de prueba primero
4. **Contactar** soporte técnico si es necesario
