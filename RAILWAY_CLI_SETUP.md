# 🚀 Despliegue Directo con Railway CLI

## OPCIÓN ALTERNATIVA: Railway CLI (Sin GitHub)

### 1. Instalar Railway CLI:
```bash
# Windows (PowerShell como administrador)
iwr -useb https://railway.app/install.ps1 | iex

# O descargar desde: https://railway.app/cli
```

### 2. Login en Railway:
```bash
railway login
```

### 3. Inicializar proyecto:
```bash
railway init
```

### 4. Configurar variables de entorno:
```bash
railway variables set SECRET_KEY="django-insecure-tu-secret-key-super-seguro"
railway variables set DEBUG="False"
railway variables set WASENDER_API_KEY="e736f86d08e73ce5ee6f209098dc701a60deb8157f26b79485f66e1249aabee6"
railway variables set WASENDER_SESSION_ID="8359"
railway variables set ENABLE_WHATSAPP_NOTIFICATIONS="True"
railway variables set NOTIFICATION_TIME_HOUR="9"
```

### 5. Agregar base de datos:
```bash
railway add postgresql
```

### 6. Desplegar:
```bash
railway up
```

## RESULTADO:
- ✅ Aplicación desplegada en Railway
- ✅ Base de datos PostgreSQL
- ✅ Variables configuradas
- ✅ URL pública disponible

## CONFIGURAR CRON:
Una vez desplegado, usar cron-job.org con la URL de Railway.
