# 🚂 DEPLOYMENT CON RAILWAY CLI

## Guía Rápida para Desplegar desde Railway CLI

---

## 📋 PASOS A SEGUIR

### 1. Verificar Railway CLI instalado
```bash
railway --version
```

### 2. Login a Railway (si no estás logueado)
```bash
railway login
```

### 3. Link al proyecto (si no está linkeado)
```bash
railway link
```

### 4. Commit y Push a Git
```bash
git add .
git commit -m "Add Call Center IA system for Ecuador"
git push origin main
```

### 5. Ejecutar Migraciones en Railway
```bash
railway run python manage.py migrate
```

### 6. Poblar Datos en Railway (opcional)
```bash
railway run python populate_callcenter_ecuador.py
```

### 7. Verificar que todo funciona
```bash
railway open
```

---

## ✅ COMANDOS COMPLETOS

Ejecuta estos comandos uno por uno:

```bash
# 1. Agregar todos los archivos
git add .

# 2. Commit
git commit -m "Add Call Center IA: models, admin, AI services for Ecuador"

# 3. Push
git push origin main

# 4. Esperar que Railway haga el build (30-60 segundos)

# 5. Ejecutar migraciones
railway run python manage.py migrate

# 6. Verificar migraciones
railway run python manage.py showmigrations callcenter

# 7. Poblar datos (opcional)
railway run python populate_callcenter_ecuador.py

# 8. Abrir la app
railway open
```

---

## 🔍 VERIFICACIÓN

```bash
# Ver logs en tiempo real
railway logs

# Verificar que callcenter está instalado
railway run python manage.py shell -c "from callcenter.models import Lead; print('OK')"

# Contar operadores
railway run python manage.py shell -c "from callcenter.models import Operador; print(f'Operadores: {Operador.objects.count()}')"

# Contar leads
railway run python manage.py shell -c "from callcenter.models import Lead; print(f'Leads: {Lead.objects.count()}')"
```

---

## ⚡ COMANDOS RÁPIDOS

```bash
# Todo en uno (después del push)
railway run python manage.py migrate && railway run python populate_callcenter_ecuador.py && railway open
```
