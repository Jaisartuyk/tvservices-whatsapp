# 🚀 Despliegue en Producción - TV Services

## 🌐 OPCIONES PARA PRODUCCIÓN (24/7)

### ⭐ OPCIÓN 1: HEROKU (Recomendado - Fácil)
**Costo**: $7-25/mes | **Configuración**: 30 minutos

#### Ventajas:
- ✅ **Siempre disponible** (24/7)
- ✅ **Cron jobs integrados** (Heroku Scheduler)
- ✅ **Base de datos incluida** (PostgreSQL)
- ✅ **SSL automático**
- ✅ **Fácil despliegue** con Git

#### Configuración:
```bash
# 1. Instalar Heroku CLI
# 2. Crear app
heroku create tvservices-whatsapp

# 3. Configurar variables de entorno
heroku config:set WASENDER_API_KEY=tu-api-key
heroku config:set WASENDER_SESSION_ID=8359
heroku config:set SECRET_KEY=tu-secret-key

# 4. Desplegar
git push heroku main

# 5. Configurar cron jobs
heroku addons:create scheduler:standard
```

#### Cron Jobs en Heroku:
```bash
# Agregar en Heroku Scheduler (cada día 9:00 AM)
python manage.py send_expiration_notifications --days 0
python manage.py send_expiration_notifications --days 1
python manage.py send_expiration_notifications --days 3
python manage.py send_expiration_notifications --days 7
```

---

### 🐧 OPCIÓN 2: VPS LINUX (DigitalOcean/AWS)
**Costo**: $5-20/mes | **Configuración**: 2 horas

#### Ventajas:
- ✅ **Control total** del servidor
- ✅ **Más económico** a largo plazo
- ✅ **Escalable**
- ✅ **Cron nativo** de Linux

#### Configuración:
```bash
# 1. Crear VPS Ubuntu 22.04
# 2. Instalar dependencias
sudo apt update
sudo apt install python3 python3-pip nginx postgresql

# 3. Clonar proyecto
git clone tu-repositorio.git
cd tvservices_project

# 4. Configurar entorno
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configurar cron
crontab -e
# Agregar:
0 9 * * * cd /home/user/tvservices_project && python manage.py send_expiration_notifications --days 0
0 9 * * * cd /home/user/tvservices_project && python manage.py send_expiration_notifications --days 1
0 9 * * * cd /home/user/tvservices_project && python manage.py send_expiration_notifications --days 3
0 9 * * * cd /home/user/tvservices_project && python manage.py send_expiration_notifications --days 7
```

---

### ☁️ OPCIÓN 3: RAILWAY (Moderno)
**Costo**: $5-15/mes | **Configuración**: 20 minutos

#### Ventajas:
- ✅ **Deploy automático** desde GitHub
- ✅ **Cron jobs** incluidos
- ✅ **Base de datos** PostgreSQL
- ✅ **Muy fácil** de usar

#### Configuración:
1. **Conectar** repositorio GitHub
2. **Configurar** variables de entorno
3. **Agregar** `railway.json`:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py runserver 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

### 🌊 OPCIÓN 4: RENDER (Gratuito/Pago)
**Costo**: Gratis o $7/mes | **Configuración**: 25 minutos

#### Ventajas:
- ✅ **Plan gratuito** disponible
- ✅ **Cron jobs** en plan pago
- ✅ **SSL automático**
- ✅ **Deploy desde Git**

---

## 🎯 RECOMENDACIÓN ESPECÍFICA PARA TI

### Para Empezar: **HEROKU** 
**¿Por qué?**
- ✅ **Más fácil** de configurar
- ✅ **Cron jobs** integrados
- ✅ **Soporte 24/7**
- ✅ **Escalable** cuando crezcas

### Configuración Heroku (Paso a Paso):

#### 1. Preparar el Proyecto:
```bash
# Crear archivos necesarios
echo "web: gunicorn tvservices.wsgi" > Procfile
echo "python-3.11.0" > runtime.txt
pip freeze > requirements.txt
```

#### 2. Configurar Base de Datos:
```python
# En settings.py agregar:
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'))
}
```

#### 3. Variables de Entorno en Heroku:
```bash
heroku config:set DEBUG=False
heroku config:set WASENDER_API_KEY=e736f86d08e73ce5ee6f209098dc701a60deb8157f26b79485f66e1249aabee6
heroku config:set WASENDER_SESSION_ID=8359
heroku config:set WASENDER_WEBHOOK_URL=https://www.iqautoec.com/webhook/whatsapp/
heroku config:set SECRET_KEY=tu-secret-key-super-seguro
```

#### 4. Configurar Scheduler:
```bash
# Instalar addon
heroku addons:create scheduler:standard

# Abrir dashboard
heroku addons:open scheduler

# Agregar jobs:
# Job 1: "0 14 * * *" (9 AM Ecuador = 2 PM UTC)
python manage.py send_expiration_notifications --days 0

# Job 2: "0 14 * * *"
python manage.py send_expiration_notifications --days 1

# Job 3: "0 14 * * *"
python manage.py send_expiration_notifications --days 3

# Job 4: "0 14 * * *"
python manage.py send_expiration_notifications --days 7
```

---

## 💰 COMPARACIÓN DE COSTOS

| Opción | Costo Mensual | Configuración | Mantenimiento |
|--------|---------------|---------------|---------------|
| **Heroku** | $7-25 | ⭐⭐⭐⭐⭐ Fácil | ⭐⭐⭐⭐⭐ Mínimo |
| **VPS** | $5-20 | ⭐⭐⭐ Medio | ⭐⭐ Requiere conocimiento |
| **Railway** | $5-15 | ⭐⭐⭐⭐ Fácil | ⭐⭐⭐⭐ Mínimo |
| **Render** | $0-7 | ⭐⭐⭐⭐ Fácil | ⭐⭐⭐⭐ Mínimo |

---

## 🚀 PLAN DE ACCIÓN RECOMENDADO

### Fase 1: Despliegue Inmediato (Hoy)
1. **Crear cuenta** en Heroku
2. **Preparar archivos** (Procfile, requirements.txt)
3. **Desplegar** aplicación
4. **Configurar** variables de entorno

### Fase 2: Automatización (Mañana)
1. **Instalar** Heroku Scheduler
2. **Configurar** 4 cron jobs
3. **Probar** envío automático
4. **Monitorear** logs

### Fase 3: Optimización (Próxima semana)
1. **Configurar** dominio personalizado
2. **Optimizar** base de datos
3. **Configurar** monitoreo
4. **Backup** automático

---

## 📞 SOPORTE PARA DESPLIEGUE

### ¿Necesitas ayuda?
- **Heroku**: Documentación excelente
- **Comunidad**: Stack Overflow
- **Soporte**: Chat en vivo (planes pagos)

### Archivos que necesitas crear:
1. `Procfile`
2. `requirements.txt` 
3. `runtime.txt`
4. Configurar `settings.py` para producción

---

## ⚡ INICIO RÁPIDO (30 MINUTOS)

```bash
# 1. Instalar Heroku CLI
# 2. Login
heroku login

# 3. Crear app
heroku create tu-app-name

# 4. Configurar variables
heroku config:set WASENDER_API_KEY=tu-key

# 5. Deploy
git add .
git commit -m "Deploy to production"
git push heroku main

# 6. Configurar scheduler
heroku addons:create scheduler:standard
```

**¡En 30 minutos tendrás tu sistema funcionando 24/7!** 🎉
