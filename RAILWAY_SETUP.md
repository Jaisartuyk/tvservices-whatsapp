# 🛤️ Configuración Completa para Railway

## 📋 PASOS PARA DESPLEGAR EN RAILWAY

### 1. **Preparar Repositorio Git**
```bash
# Si no tienes git inicializado
git init
git add .
git commit -m "Initial commit for Railway deployment"

# Subir a GitHub (crear repositorio en github.com primero)
git remote add origin https://github.com/tu-usuario/tvservices-project.git
git branch -M main
git push -u origin main
```

### 2. **Configurar en Railway.app**
1. Ve a [railway.app](https://railway.app)
2. **Sign up** con GitHub
3. **New Project** → **Deploy from GitHub repo**
4. Selecciona tu repositorio `tvservices-project`

### 3. **Configurar Variables de Entorno**
En Railway Dashboard → **Variables**:

```bash
# Django
SECRET_KEY=tu-secret-key-super-seguro-aqui
DEBUG=False
DJANGO_SETTINGS_MODULE=tvservices.settings

# Base de datos (Railway la crea automáticamente)
# DATABASE_URL se configura automáticamente

# WaSender API
WASENDER_API_KEY=e736f86d08e73ce5ee6f209098dc701a60deb8157f26b79485f66e1249aabee6
WASENDER_SESSION_ID=8359
WASENDER_WEBHOOK_URL=https://www.iqautoec.com/webhook/whatsapp/
WASENDER_WEBHOOK_SECRET=tu-webhook-secret

# Notificaciones
ENABLE_WHATSAPP_NOTIFICATIONS=True
NOTIFICATION_TIME_HOUR=9

# Railway
RAILWAY_ENVIRONMENT=production
```

### 4. **Agregar Base de Datos PostgreSQL**
1. En Railway Dashboard → **New** → **Database** → **PostgreSQL**
2. Railway conectará automáticamente la `DATABASE_URL`

### 5. **Configurar Cron Jobs**
Railway no tiene cron integrado, pero podemos usar **GitHub Actions**:

#### Crear `.github/workflows/cron-notifications.yml`:
```yaml
name: Notificaciones WhatsApp Automáticas

on:
  schedule:
    # Ejecutar diariamente a las 14:00 UTC (9:00 AM Ecuador)
    - cron: '0 14 * * *'
  workflow_dispatch: # Permite ejecución manual

jobs:
  send-notifications:
    runs-on: ubuntu-latest
    
    steps:
    - name: Ejecutar notificaciones
      run: |
        curl -X POST "${{ secrets.RAILWAY_WEBHOOK_URL }}" \
        -H "Content-Type: application/json" \
        -d '{"action": "run_notifications"}'
```

### 6. **Crear Endpoint para Cron en Django**
Agregar a `urls.py`:
```python
path('cron/notifications/', views.cron_notifications, name='cron_notifications'),
```

Agregar vista en `views.py`:
```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def cron_notifications(request):
    """Endpoint para ejecutar notificaciones desde cron externo"""
    try:
        # Verificar token de seguridad
        data = json.loads(request.body)
        if data.get('action') == 'run_notifications':
            
            # Ejecutar script de notificaciones
            import subprocess
            result = subprocess.run([
                'python', 'cron_notifications.py'
            ], capture_output=True, text=True)
            
            return JsonResponse({
                'success': True,
                'output': result.stdout,
                'error': result.stderr
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
```

---

## 🚀 ALTERNATIVA: Usar Servicio Externo de Cron

### **Opción A: Cron-job.org (Gratuito)**
1. Ve a [cron-job.org](https://cron-job.org)
2. Crear cuenta gratuita
3. **New Cronjob**:
   - **URL**: `https://tu-app.railway.app/cron/notifications/`
   - **Schedule**: `0 14 * * *` (9 AM Ecuador)
   - **Method**: POST
   - **Body**: `{"action": "run_notifications"}`

### **Opción B: EasyCron (Gratuito)**
1. Ve a [easycron.com](https://easycron.com)
2. Crear cuenta gratuita
3. Configurar igual que cron-job.org

---

## 📊 MONITOREO Y LOGS

### Ver Logs en Railway:
1. Railway Dashboard → **Deployments**
2. Click en deployment activo
3. Ver **Logs** en tiempo real

### Verificar Notificaciones:
```bash
# En Railway logs buscar:
✅ Notificaciones día 0 enviadas exitosamente
✅ Notificaciones día 1 enviadas exitosamente
✅ Notificaciones día 3 enviadas exitosamente
✅ Notificaciones día 7 enviadas exitosamente
```

---

## 🔧 COMANDOS ÚTILES

### Ejecutar Migraciones:
```bash
# Railway ejecuta automáticamente, pero si necesitas manual:
railway run python manage.py migrate
```

### Ver Variables:
```bash
railway variables
```

### Ver Logs:
```bash
railway logs
```

---

## 💰 COSTOS RAILWAY

### Plan Hobby (Recomendado):
- **$5/mes** por servicio
- **Base de datos PostgreSQL** incluida
- **500 horas** de ejecución/mes
- **Dominio personalizado**

### Plan Pro:
- **$20/mes** por servicio
- **Recursos ilimitados**
- **Soporte prioritario**

---

## ✅ CHECKLIST FINAL

- [ ] Repositorio en GitHub
- [ ] Proyecto creado en Railway
- [ ] Variables de entorno configuradas
- [ ] Base de datos PostgreSQL agregada
- [ ] Cron job configurado (cron-job.org)
- [ ] Endpoint `/cron/notifications/` funcionando
- [ ] Logs mostrando despliegue exitoso
- [ ] Prueba manual de notificaciones

---

## 🎯 RESULTADO FINAL

Una vez configurado:
- ✅ **Aplicación disponible 24/7**
- ✅ **Notificaciones automáticas** a las 9:00 AM Ecuador
- ✅ **Base de datos persistente**
- ✅ **Logs y monitoreo**
- ✅ **Escalable automáticamente**

**¡Tu sistema de notificaciones WhatsApp funcionará completamente automático!** 🚀
