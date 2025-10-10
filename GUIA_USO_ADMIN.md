# 🎯 GUÍA DE USO DEL ADMIN - CALL CENTER IA

## 📋 Módulos Disponibles

---

## 🔥 EXPLORAR EL SISTEMA

### 1. 📱 **OPERADORES** (Click aquí primero)

**Qué verás:**
- ✅ Claro Ecuador (Rojo)
- ✅ Movistar Ecuador (Azul)
- ✅ CNT (Azul oscuro)
- ✅ Tuenti Ecuador (Cyan)

**Información de cada operador:**
- Logo y color corporativo
- Teléfono de atención
- Sitio web
- Número de productos activos

---

### 2. 📦 **PRODUCTOS** (Explora los planes)

**Qué verás:**
- 32 productos configurados
- Filtros por operador y tipo
- Precios con descuentos
- Badges de productos destacados ⭐

**Tipos de productos:**
- 🌐 Internet Hogar (20, 50, 100 Mbps)
- 📱 Planes Móviles (5GB, 10GB, 20GB)
- 📺 TV por Cable (Básico, Premium)
- 📦 Combos (Familiar, Total)

**Ejemplo:**
```
Claro Ecuador Internet 50 Mbps
Precio: $29.75 (antes $35.00)
Velocidad: 50 Mbps
Zonas: Guayaquil, Quito, Cuenca, Manta, Ambato
```

---

### 3. 👥 **LEADS** (¡Lo más importante!)

**Qué verás:**
- 8 leads de ejemplo
- Clasificación por colores:
  - 🔥 **Rojo** = HOT (Listo para comprar)
  - 🌡️ **Amarillo** = WARM (Interesado)
  - ❄️ **Gris** = COLD (Solo preguntando)

**Leads HOT que debes ver:**

#### 1. Carlos Mendoza 🔥
- **Zona:** Urdesa, Guayaquil
- **Teléfono:** +593987654321
- **Score:** 95
- **Interés:** Internet 50 Mbps
- **Estado:** Negociando
- **Nota:** "Cliente muy interesado, quiere contratar esta semana"

#### 2. María Rodríguez 🔥
- **Zona:** La Carolina, Quito
- **Teléfono:** +593987654322
- **Score:** 90
- **Interés:** Combo Total
- **Estado:** Calificado
- **Nota:** "Quiere combo completo, ya tiene fecha de instalación"

**Filtros útiles:**
- Por clasificación (HOT/WARM/COLD)
- Por estado (Nuevo, Contactado, Negociando)
- Por fuente (WhatsApp, Llamada, Web)
- Por agente asignado

**Acciones disponibles:**
- 🔥 Marcar como HOT
- 🌡️ Marcar como WARM
- ❄️ Marcar como COLD
- 🔄 Actualizar Scores

---

### 4. 💬 **CONVERSACIONES**

**Qué verás:**
- 6 conversaciones de ejemplo
- Análisis de sentimiento (😊 😐 😞)
- Canal (WhatsApp, Llamada)
- Intenciones detectadas

**Ejemplo de conversación:**

```
Lead: Carlos Mendoza
Canal: WhatsApp
Sentimiento: 😊 Positivo

Cliente: "Hola, quiero contratar internet de 50 megas para mi casa en Urdesa"

Sistema: "¡Hola Carlos! 👋 Excelente elección. Tenemos el plan perfecto 
para Urdesa. El plan de 50 Mbps está en promoción a $29.75/mes. ¿Te interesa?"

Intenciones detectadas:
- INTERES_COMPRA
- CONSULTA_TECNICA
- CONSULTA_DISPONIBILIDAD
```

---

### 5. 📞 **LLAMADAS IA**

**Qué verás:**
- Registro de llamadas
- Duración
- Resultado (Exitosa, No contesta, Buzón)
- Transcripciones
- Análisis automático

---

### 6. 💰 **VENTAS**

**Qué verás:**
- 1 venta de ejemplo
- Lead: Carlos Mendoza
- Producto: Internet 50 Mbps
- Precio: $29.75
- Estado: Pendiente de instalación
- Fecha de instalación programada

---

## 🎯 ACCIONES QUE PUEDES HACER

### En LEADS:

#### 1. Ver Detalle de un Lead
- Click en el nombre del lead
- Verás toda su información
- Historial de conversaciones
- Score y clasificación
- Próxima acción sugerida

#### 2. Crear un Nuevo Lead
- Click en "Añadir Lead"
- Llenar información básica:
  - Nombre y apellido
  - Teléfono (+593...)
  - Zona (ej: Urdesa, Guayaquil)
  - Tipo de servicio de interés
- El sistema calculará el score automáticamente

#### 3. Filtrar Leads
- **Por clasificación:** Ver solo HOT leads
- **Por estado:** Ver leads en negociación
- **Por zona:** Ver leads de Guayaquil
- **Por agente:** Ver tus leads asignados

#### 4. Acciones Masivas
- Selecciona varios leads
- En "Acción": 
  - Marcar como HOT
  - Marcar como WARM
  - Marcar como COLD
  - Actualizar Scores

---

### En PRODUCTOS:

#### 1. Ver Productos por Operador
- Filtrar por: Claro Ecuador
- Ver todos los planes de Claro

#### 2. Ver Productos Destacados
- Filtrar por: "Plan Destacado" = Sí
- Ver los mejores planes

#### 3. Ver por Tipo de Servicio
- Internet Hogar
- Planes Móviles
- TV por Cable
- Combos

---

### En CONVERSACIONES:

#### 1. Ver Conversaciones por Lead
- Buscar por nombre del lead
- Ver todo el historial

#### 2. Filtrar por Sentimiento
- Ver solo conversaciones positivas
- Identificar clientes satisfechos

#### 3. Filtrar por Canal
- WhatsApp
- Llamadas
- Email

---

## 📊 MÉTRICAS Y ESTADÍSTICAS

### Dashboard Principal:
```
Call Center IA
├─ Operadores: 4
├─ Productos: 32
├─ Leads: 8
│  ├─ HOT: 2 🔥
│  ├─ WARM: 3 🌡️
│  └─ COLD: 3 ❄️
├─ Conversaciones: 6
├─ Llamadas IA: 0
└─ Ventas: 1
```

---

## 🎯 FLUJO DE TRABAJO RECOMENDADO

### 1. **Revisar Leads HOT** (Prioridad Alta)
```
Admin → Leads → Filtrar por "HOT"
→ Ver Carlos Mendoza y María Rodríguez
→ Contactar inmediatamente
```

### 2. **Revisar Leads WARM** (Prioridad Media)
```
Admin → Leads → Filtrar por "WARM"
→ Ver Juan, Ana, Luis
→ Agendar seguimiento
```

### 3. **Ver Conversaciones Recientes**
```
Admin → Conversaciones
→ Ver últimas interacciones
→ Identificar oportunidades
```

### 4. **Registrar Nueva Venta**
```
Admin → Ventas → Añadir
→ Seleccionar lead
→ Seleccionar producto
→ Ingresar precio y detalles
```

---

## 💡 TIPS DE USO

### 1. **Scoring Automático**
- El sistema calcula el score automáticamente
- Basado en: producto de interés, presupuesto, conversaciones
- Score 80-100 = HOT 🔥
- Score 50-79 = WARM 🌡️
- Score 0-49 = COLD ❄️

### 2. **Clasificación por Colores**
- Rojo = Urgente, contactar YA
- Amarillo = Seguimiento en 24h
- Gris = Campaña de nurturing

### 3. **Filtros Rápidos**
- Usa los filtros laterales
- Combina múltiples filtros
- Guarda búsquedas frecuentes

### 4. **Búsqueda Inteligente**
- Busca por nombre, teléfono, zona
- Busca en conversaciones
- Busca en notas

---

## 🚀 PRÓXIMOS PASOS

### Ahora que conoces el admin:

1. ✅ **Explora cada módulo**
   - Click en "Operadores"
   - Click en "Productos"
   - Click en "Leads"

2. ✅ **Revisa los Leads HOT**
   - Carlos Mendoza (Score 95)
   - María Rodríguez (Score 90)

3. ✅ **Lee las Conversaciones**
   - Ver cómo interactúa el bot
   - Ver análisis de sentimiento

4. 🔜 **Crea tu Primer Lead Real**
   - Click en "Añadir Lead"
   - Ingresa datos reales
   - El sistema lo clasificará automáticamente

5. 🔜 **Configura WhatsApp**
   - Para recibir mensajes reales
   - Integrar con Twilio

---

## 📱 EJEMPLO: CREAR UN LEAD NUEVO

### Paso a Paso:

1. **Ir a Leads**
   ```
   Admin → Call Center IA → Leads → Añadir Lead
   ```

2. **Información Personal**
   ```
   Nombre: Roberto
   Apellido: Gómez
   Teléfono: +593987654329
   Email: roberto.gomez@email.com
   Zona: Samborondón
   ```

3. **Intereses**
   ```
   Tipo de servicio: Internet
   Presupuesto: $40
   ```

4. **Guardar**
   - El sistema calculará el score automáticamente
   - Lo clasificará como HOT/WARM/COLD
   - Sugerirá la próxima acción

---

## 🎨 CARACTERÍSTICAS DEL ADMIN

### Badges de Colores:
- 🔴 HOT = Rojo
- 🟡 WARM = Amarillo
- ⚪ COLD = Gris
- 😊 Positivo = Verde
- 😐 Neutral = Gris
- 😞 Negativo = Rojo

### Barras de Progreso:
- Score visual con barra de color
- Fácil identificación de leads calientes

### Filtros Avanzados:
- Por clasificación
- Por estado
- Por fuente
- Por agente
- Por fecha

---

## 🎉 ¡EXPLORA EL SISTEMA!

### Comienza por:
1. **Click en "Leads"** → Ver los 8 leads
2. **Click en "Carlos Mendoza"** → Ver lead HOT
3. **Click en "Conversaciones"** → Ver interacciones
4. **Click en "Productos"** → Ver planes disponibles

---

## 📞 ACCESO RÁPIDO

```
Admin Principal:
https://tvservices-whatsapp-production.up.railway.app/admin/

Módulos Directos:
/admin/callcenter/lead/ ← Empieza aquí
/admin/callcenter/operador/
/admin/callcenter/producto/
/admin/callcenter/conversacion/
/admin/callcenter/venta/
```

---

## 🎯 **¡AHORA EXPLORA TU SISTEMA!**

**Empieza por ver los Leads HOT:** 
👉 Click en "Leads" → Filtrar por "HOT"

**¡Disfruta tu nuevo Call Center con IA!** 🚀🇪🇨
