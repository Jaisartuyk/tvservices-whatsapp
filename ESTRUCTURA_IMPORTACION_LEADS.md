# 📋 Estructura para Importación de Leads

## 📁 Formato de Archivo

Puedes usar **CSV** o **Excel (.xlsx)**

---

## 📊 Columnas Requeridas

### **Estructura del archivo:**

```csv
nombre,apellido,telefono,email,zona,operador,tipo_servicio,presupuesto,notas
```

---

## 📝 Descripción de Columnas

| Columna | Tipo | Requerido | Descripción | Ejemplo |
|---------|------|-----------|-------------|---------|
| **nombre** | Texto | ✅ Sí | Nombre del lead | Juan |
| **apellido** | Texto | ✅ Sí | Apellido del lead | Pérez |
| **telefono** | Texto | ✅ Sí | Teléfono (con o sin +593) | 0998765432 |
| **email** | Email | ❌ No | Correo electrónico | juan@email.com |
| **zona** | Texto | ✅ Sí | Zona o distrito | Norte de Guayaquil |
| **operador** | Texto | ❌ No | Operador de interés | Claro |
| **tipo_servicio** | Texto | ❌ No | Tipo de servicio | INTERNET |
| **presupuesto** | Número | ❌ No | Presupuesto estimado | 50.00 |
| **notas** | Texto | ❌ No | Notas adicionales | Cliente muy interesado |

---

## 🎯 Valores Válidos

### **tipo_servicio:**
- `INTERNET` - Internet Hogar
- `MOVIL` - Plan Móvil
- `TV` - TV por Cable
- `TELEFONIA` - Telefonía Fija
- `COMBO` - Paquete Combo

### **operador:**
- `Claro`
- `Movistar`
- `CNT`
- O cualquier operador que tengas registrado

---

## 📄 Ejemplo de Archivo CSV

```csv
nombre,apellido,telefono,email,zona,operador,tipo_servicio,presupuesto,notas
Juan,Pérez,0998765432,juan@email.com,Norte de Guayaquil,Claro,INTERNET,50.00,Cliente interesado en fibra óptica
María,González,0987654321,maria@email.com,Centro,Movistar,COMBO,80.00,Quiere internet + TV
Carlos,Rodríguez,0976543210,,Sur,CNT,MOVIL,30.00,Solo plan móvil
Ana,Martínez,0965432109,ana@email.com,Norte,,INTERNET,45.00,
Pedro,López,0954321098,pedro@email.com,Este,Claro,TV,25.00,Interesado en canales premium
```

---

## 📄 Ejemplo de Archivo Excel

Crea un archivo Excel con las mismas columnas en la primera fila:

| nombre | apellido | telefono | email | zona | operador | tipo_servicio | presupuesto | notas |
|--------|----------|----------|-------|------|----------|---------------|-------------|-------|
| Juan | Pérez | 0998765432 | juan@email.com | Norte de Guayaquil | Claro | INTERNET | 50.00 | Cliente interesado |
| María | González | 0987654321 | maria@email.com | Centro | Movistar | COMBO | 80.00 | Quiere internet + TV |

---

## ⚙️ Comportamiento del Sistema

### **Al importar, el sistema:**

1. ✅ **Valida** que el teléfono no esté duplicado
2. ✅ **Normaliza** el teléfono (agrega +593 si es necesario)
3. ✅ **Busca** el operador por nombre (si existe)
4. ✅ **Asigna** clasificación COLD por defecto
5. ✅ **Asigna** estado NUEVO por defecto
6. ✅ **Asigna** fuente WEB por defecto
7. ✅ **Calcula** score inicial (30 puntos)

### **Si falta información:**
- Si no hay **operador**, usa el operador por defecto del formulario
- Si no hay **email**, lo deja vacío
- Si no hay **presupuesto**, lo deja en NULL
- Si no hay **notas**, lo deja vacío

---

## 🚀 Cómo Usar

1. **Prepara tu archivo** CSV o Excel con la estructura indicada
2. **Ve a** `/callcenter/leads/`
3. **Click en** botón "Importar"
4. **Selecciona** el archivo
5. **Elige** operador por defecto (opcional)
6. **Click en** "Importar"
7. **Espera** la confirmación

---

## ✅ Resultado

El sistema te mostrará:
- ✅ Número de leads importados exitosamente
- ⚠️ Leads duplicados (no importados)
- ❌ Errores encontrados

---

## 📝 Notas Importantes

- El teléfono debe ser único (no se importarán duplicados)
- Los nombres de operadores deben coincidir exactamente con los registrados
- Los tipos de servicio deben usar los códigos exactos (INTERNET, MOVIL, etc.)
- El archivo puede tener hasta 1000 leads por importación
- Formato de teléfono: 10 dígitos o con +593

---

## 🔧 Solución de Problemas

### **Error: "Teléfono duplicado"**
- El lead ya existe en la base de datos
- Verifica que no esté importando el mismo archivo dos veces

### **Error: "Operador no encontrado"**
- El nombre del operador no coincide
- Usa el operador por defecto del formulario

### **Error: "Tipo de servicio inválido"**
- Usa solo los valores permitidos: INTERNET, MOVIL, TV, TELEFONIA, COMBO

---

## 📞 Soporte

Si tienes problemas con la importación, contacta al administrador del sistema.
