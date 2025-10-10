# 🇪🇨 CONFIGURACIÓN PARA ECUADOR

## ✅ Sistema Adaptado para Ecuador - Guayaquil

---

## 📱 **OPERADORES DE ECUADOR**

### 1. **Claro Ecuador**
- Color: Rojo (#E30613)
- Atención: *611
- Web: https://www.claro.com.ec

### 2. **Movistar Ecuador**
- Color: Azul (#019DF4)
- Atención: *150
- Web: https://www.movistar.com.ec

### 3. **CNT (Corporación Nacional de Telecomunicaciones)**
- Color: Azul (#0066CC)
- Atención: 1800-266-826
- Web: https://www.cnt.gob.ec

### 4. **Tuenti Ecuador**
- Color: Cyan (#00D9FF)
- Atención: *611
- Web: https://www.tuenti.ec

---

## 📦 **PRODUCTOS CONFIGURADOS**

### Internet Hogar
- 20 Mbps - $25/mes
- 50 Mbps - $35/mes ⭐
- 100 Mbps - $50/mes

### Planes Móviles
- 5GB - $15/mes
- 10GB - $20/mes ⭐
- 20GB - $30/mes

### TV por Cable
- TV Básico (60 canales) - $20/mes
- TV Premium (120 canales) - $35/mes ⭐

### Combos
- Combo Familiar - $55/mes ⭐
  - Internet 50 Mbps + TV 80 canales + Teléfono
- Combo Total - $75/mes ⭐
  - Internet 100 Mbps + TV 120 canales + Teléfono + Netflix 3 meses

---

## 🌍 **ZONAS DE COBERTURA**

### Principales Ciudades:
- ✅ Guayaquil (Urdesa, Kennedy, Alborada, Samborondón)
- ✅ Quito (La Carolina, El Batán, Cumbayá)
- ✅ Cuenca
- ✅ Manta
- ✅ Ambato

---

## 👥 **LEADS DE EJEMPLO**

### 🔥 HOT Leads (2)
1. **Carlos Mendoza** - Urdesa, Guayaquil
   - Interés: Internet 50 Mbps
   - Score: 95
   - Estado: Negociando

2. **María Rodríguez** - La Carolina, Quito
   - Interés: Combo Total
   - Score: 90
   - Estado: Calificado

### 🌡️ WARM Leads (3)
3. **Juan Pérez** - Kennedy Norte, Guayaquil
   - Interés: Plan Móvil 10GB
   - Score: 65

4. **Ana Torres** - El Batán, Quito
   - Interés: Internet
   - Score: 55

5. **Luis Vásquez** - Samborondón
   - Interés: Combo Familiar
   - Score: 60

### ❄️ COLD Leads (3)
6. **Pedro Sánchez** - Alborada, Guayaquil
   - Score: 30

7. **Laura Martínez** - Cumbayá, Quito
   - Score: 25

8. **Diego Flores** - Cuenca Centro
   - Score: 20

---

## ⏰ **ZONA HORARIA**

### Configuración:
- **Zona Horaria**: America/Guayaquil
- **GMT**: -5
- **Horario**: Ecuador Continental

### Características:
- ✅ Todas las fechas y horas en hora de Ecuador
- ✅ Última interacción con timestamp local
- ✅ Fechas de instalación en calendario ecuatoriano

---

## 📞 **FORMATO DE TELÉFONOS**

### Código de País: +593

**Ejemplos:**
- Guayaquil: +593987654321
- Quito: +593987654322
- Cuenca: +593987654328

---

## 💬 **CONVERSACIONES DE EJEMPLO**

### Contexto Ecuatoriano:

**Cliente de Guayaquil:**
> "Hola, quiero contratar internet de 50 megas para mi casa en Urdesa"

**Bot responde:**
> "¡Hola Carlos! 👋 Excelente elección. Tenemos el plan perfecto para Urdesa. 
> El plan de 50 Mbps está en promoción a $29.75/mes. ¿Te interesa?"

**Cliente de Quito:**
> "Buenos días, quiero información sobre paquetes combo en La Carolina"

**Bot responde:**
> "Buenos días María! Con gusto. Para La Carolina tenemos el Combo Familiar 
> a $44/mes con Internet 50 Mbps + TV + Teléfono."

---

## 🚀 **CÓMO USAR**

### Paso 1: Activar la app callcenter

Edita `tvservices/settings.py`:

```python
INSTALLED_APPS = [
    # ... apps existentes ...
    'callcenter',  # ← AGREGAR
]

# Configurar zona horaria de Ecuador
TIME_ZONE = 'America/Guayaquil'
USE_TZ = True
```

### Paso 2: Instalar pytz (para zona horaria)

```bash
pip install pytz
```

Agrega a `requirements.txt`:
```
pytz>=2023.3
```

### Paso 3: Crear migraciones

```bash
python manage.py makemigrations callcenter
python manage.py migrate
```

### Paso 4: Poblar con datos de Ecuador

```bash
python populate_callcenter_ecuador.py
```

### Paso 5: Verificar

```bash
python manage.py runserver
```

Accede a: `http://localhost:8000/admin/`

---

## 📊 **DATOS CREADOS**

Al ejecutar el script verás:

```
🇪🇨 POBLANDO BASE DE DATOS - CALL CENTER IA ECUADOR
================================================================================
📅 Fecha y hora Ecuador: 10/10/2025 13:09:30 -05
🌍 Zona horaria: America/Guayaquil (GMT-5)
================================================================================

📱 Creando operadores de Ecuador...
  ✅ Creado: Claro Ecuador
  ✅ Creado: Movistar Ecuador
  ✅ Creado: CNT (Corporación Nacional de Telecomunicaciones)
  ✅ Creado: Tuenti Ecuador

📦 Creando productos para Ecuador...
  ✅ Claro Ecuador Internet 20 Mbps
  ✅ Claro Ecuador Internet 50 Mbps
  ... (más productos)

👥 Creando leads de Ecuador...
  ✅ Carlos Mendoza - 🔥 Hot Lead - Urdesa, Guayaquil
  ✅ María Rodríguez - 🔥 Hot Lead - La Carolina, Quito
  ... (más leads)

💬 Creando conversaciones...
  ✅ Conversación con Carlos Mendoza - WhatsApp
  ... (más conversaciones)

💰 Creando ventas...
  ✅ Venta a Carlos Mendoza - $29.75

================================================================================
✅ DATOS CREADOS EXITOSAMENTE PARA ECUADOR
================================================================================
📱 Operadores: 4
   • Claro Ecuador
   • Movistar Ecuador
   • CNT
   • Tuenti Ecuador

📦 Productos: 32
👥 Leads: 8
   🔥 HOT: 2
   🌡️  WARM: 3
   ❄️  COLD: 3
💬 Conversaciones: 6
💰 Ventas: 1
================================================================================
```

---

## 💡 **DIFERENCIAS CON VERSIÓN PERÚ**

| Aspecto | Perú | Ecuador |
|---------|------|---------|
| Operadores | Claro, Movistar, Entel, Bitel | Claro EC, Movistar EC, CNT, Tuenti |
| Código País | +51 | +593 |
| Ciudades | Lima, Arequipa | Guayaquil, Quito, Cuenca |
| Zona Horaria | America/Lima | America/Guayaquil |
| Moneda | S/ (Soles) | $ (Dólares) |
| Atención Claro | 123 | *611 |
| Atención Movistar | 104 | *150 |

---

## 🎯 **PRÓXIMOS PASOS**

1. ✅ Ejecutar script de población
2. ✅ Verificar datos en admin
3. 🔜 Configurar WhatsApp Business API Ecuador
4. 🔜 Integrar con operadores locales
5. 🔜 Personalizar mensajes para Ecuador

---

## 📝 **NOTAS IMPORTANTES**

### Precios en Dólares
- Ecuador usa dólares estadounidenses ($)
- Todos los precios están en USD
- No se requiere conversión de moneda

### Horario de Atención
- Lunes a Viernes: 8:00 AM - 8:00 PM
- Sábados: 9:00 AM - 6:00 PM
- Domingos: 10:00 AM - 2:00 PM
- (Hora de Ecuador - GMT-5)

### Zonas de Cobertura
- Costa: Guayaquil, Manta, Machala
- Sierra: Quito, Cuenca, Ambato, Riobamba
- Oriente: Limitada (verificar por zona)

---

## 🆘 **SOPORTE**

### Archivos Relacionados:
- `populate_callcenter_ecuador.py` - Script de población
- `callcenter/models.py` - Modelos de datos
- `callcenter/ai_services.py` - Servicios de IA
- `PROPUESTA_CALLCENTER_IA.md` - Propuesta completa

### Comandos Útiles:
```bash
# Ver datos creados
python manage.py shell
>>> from callcenter.models import Operador, Lead
>>> Operador.objects.all()
>>> Lead.objects.filter(zona__contains='Guayaquil')

# Verificar zona horaria
>>> from django.utils import timezone
>>> timezone.now()
```

---

## 🎉 **¡LISTO PARA ECUADOR!**

El sistema está completamente configurado para operar en Ecuador con:
- ✅ Operadores ecuatorianos
- ✅ Ciudades y zonas de Ecuador
- ✅ Teléfonos con código +593
- ✅ Zona horaria de Guayaquil
- ✅ Precios en dólares
- ✅ Leads de ejemplo con datos reales

**¡Ahora puedes comenzar a vender servicios de telecomunicaciones en Ecuador!** 🇪🇨🚀
