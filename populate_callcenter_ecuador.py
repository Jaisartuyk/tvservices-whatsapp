#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo del Call Center
Configurado para ECUADOR - Guayaquil
Crea operadores, productos, leads y conversaciones de prueba
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import pytz

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from callcenter.models import (
    Operador, Producto, Lead, Conversacion, LlamadaIA, Venta,
    TipoServicio, ClasificacionLead, EstadoLead, FuenteLead,
    CanalConversacion, TipoConversacion, SentimientoConversacion,
    ResultadoLlamada, EstadoVenta
)

# Configurar zona horaria de Ecuador
ECUADOR_TZ = pytz.timezone('America/Guayaquil')


def get_ecuador_time():
    """Retorna la hora actual de Ecuador"""
    return timezone.now().astimezone(ECUADOR_TZ)


def crear_operadores():
    """Crea los operadores de telecomunicaciones de Ecuador"""
    print("\n📱 Creando operadores de Ecuador...")
    
    operadores_data = [
        {
            'nombre': 'Claro Ecuador',
            'color_principal': '#E30613',
            'sitio_web': 'https://www.claro.com.ec',
            'telefono_atencion': '*611',
            'orden': 1
        },
        {
            'nombre': 'Movistar Ecuador',
            'color_principal': '#019DF4',
            'sitio_web': 'https://www.movistar.com.ec',
            'telefono_atencion': '*150',
            'orden': 2
        },
        {
            'nombre': 'CNT (Corporación Nacional de Telecomunicaciones)',
            'color_principal': '#0066CC',
            'sitio_web': 'https://www.cnt.gob.ec',
            'telefono_atencion': '1800-266-826',
            'orden': 3
        },
        {
            'nombre': 'Tuenti Ecuador',
            'color_principal': '#00D9FF',
            'sitio_web': 'https://www.tuenti.ec',
            'telefono_atencion': '*611',
            'orden': 4
        },
    ]
    
    operadores = []
    for data in operadores_data:
        operador, created = Operador.objects.get_or_create(
            nombre=data['nombre'],
            defaults=data
        )
        operadores.append(operador)
        if created:
            print(f"  ✅ Creado: {operador.nombre}")
        else:
            print(f"  ℹ️  Ya existe: {operador.nombre}")
    
    return operadores


def crear_productos(operadores):
    """Crea productos de ejemplo para cada operador ecuatoriano"""
    print("\n📦 Creando productos para Ecuador...")
    
    productos_creados = 0
    
    for operador in operadores:
        # Internet Hogar
        productos_internet = [
            {
                'nombre_plan': f'{operador.nombre} Internet 20 Mbps',
                'tipo': TipoServicio.INTERNET,
                'velocidad_mbps': 20,
                'precio_mensual': Decimal('25.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('10.00'),
                'beneficios': ['20 Mbps de velocidad', 'Router WiFi incluido', 'Instalación gratis'],
                'zonas_disponibles': 'Guayaquil, Quito, Cuenca',
            },
            {
                'nombre_plan': f'{operador.nombre} Internet 50 Mbps',
                'tipo': TipoServicio.INTERNET,
                'velocidad_mbps': 50,
                'precio_mensual': Decimal('35.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('15.00'),
                'beneficios': ['50 Mbps de velocidad', 'Router WiFi Dual Band', 'Instalación gratis', 'Soporte 24/7'],
                'zonas_disponibles': 'Guayaquil, Quito, Cuenca, Manta, Ambato',
                'is_destacado': True,
            },
            {
                'nombre_plan': f'{operador.nombre} Internet 100 Mbps',
                'tipo': TipoServicio.INTERNET,
                'velocidad_mbps': 100,
                'precio_mensual': Decimal('50.00'),
                'precio_instalacion': Decimal('30.00'),
                'descuento_porcentaje': Decimal('20.00'),
                'beneficios': ['100 Mbps de velocidad', 'Router WiFi 6', 'Instalación gratis', 'Soporte premium 24/7', 'IP fija'],
                'zonas_disponibles': 'Principales ciudades de Ecuador',
            },
        ]
        
        # Planes Móviles
        productos_movil = [
            {
                'nombre_plan': f'{operador.nombre} Móvil 5GB',
                'tipo': TipoServicio.MOVIL,
                'gigas_datos': 5,
                'minutos_llamadas': 300,
                'precio_mensual': Decimal('15.00'),
                'precio_instalacion': Decimal('0.00'),
                'beneficios': ['5 GB de datos', '300 minutos', 'Redes sociales ilimitadas'],
                'zonas_disponibles': 'Cobertura nacional Ecuador',
            },
            {
                'nombre_plan': f'{operador.nombre} Móvil 10GB',
                'tipo': TipoServicio.MOVIL,
                'gigas_datos': 10,
                'minutos_llamadas': 500,
                'precio_mensual': Decimal('20.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('10.00'),
                'beneficios': ['10 GB de datos', '500 minutos', 'Redes sociales ilimitadas', 'WhatsApp ilimitado'],
                'zonas_disponibles': 'Cobertura nacional Ecuador',
                'is_destacado': True,
            },
            {
                'nombre_plan': f'{operador.nombre} Móvil 20GB',
                'tipo': TipoServicio.MOVIL,
                'gigas_datos': 20,
                'minutos_llamadas': 1000,
                'precio_mensual': Decimal('30.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('15.00'),
                'beneficios': ['20 GB de datos', '1000 minutos', 'Redes sociales ilimitadas', 'Roaming incluido'],
                'zonas_disponibles': 'Cobertura nacional Ecuador',
            },
        ]
        
        # TV por Cable
        productos_tv = [
            {
                'nombre_plan': f'{operador.nombre} TV Básico',
                'tipo': TipoServicio.TV,
                'canales_tv': 60,
                'precio_mensual': Decimal('20.00'),
                'precio_instalacion': Decimal('35.00'),
                'beneficios': ['60 canales', 'HD incluido', 'Decodificador incluido'],
                'zonas_disponibles': 'Guayaquil, Quito, Cuenca',
            },
            {
                'nombre_plan': f'{operador.nombre} TV Premium',
                'tipo': TipoServicio.TV,
                'canales_tv': 120,
                'precio_mensual': Decimal('35.00'),
                'precio_instalacion': Decimal('35.00'),
                'descuento_porcentaje': Decimal('10.00'),
                'beneficios': ['120 canales', 'HD y 4K', 'Canales deportivos', 'Películas premium'],
                'zonas_disponibles': 'Principales ciudades',
                'is_destacado': True,
            },
        ]
        
        # Combos
        productos_combo = [
            {
                'nombre_plan': f'{operador.nombre} Combo Familiar',
                'tipo': TipoServicio.COMBO,
                'velocidad_mbps': 50,
                'canales_tv': 80,
                'minutos_llamadas': 500,
                'precio_mensual': Decimal('55.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('20.00'),
                'beneficios': [
                    'Internet 50 Mbps',
                    '80 canales de TV',
                    'Telefonía fija ilimitada',
                    'Router WiFi incluido',
                    'Instalación gratis'
                ],
                'zonas_disponibles': 'Guayaquil, Quito, Cuenca',
                'is_destacado': True,
            },
            {
                'nombre_plan': f'{operador.nombre} Combo Total',
                'tipo': TipoServicio.COMBO,
                'velocidad_mbps': 100,
                'canales_tv': 120,
                'minutos_llamadas': 1000,
                'precio_mensual': Decimal('75.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('25.00'),
                'beneficios': [
                    'Internet 100 Mbps',
                    '120 canales de TV HD',
                    'Telefonía fija ilimitada',
                    'Router WiFi 6',
                    'Instalación gratis',
                    'Netflix incluido 3 meses'
                ],
                'zonas_disponibles': 'Principales ciudades de Ecuador',
                'is_destacado': True,
            },
        ]
        
        # Crear todos los productos
        todos_productos = productos_internet + productos_movil + productos_tv + productos_combo
        
        for prod_data in todos_productos:
            prod_data['operador'] = operador
            producto, created = Producto.objects.get_or_create(
                nombre_plan=prod_data['nombre_plan'],
                defaults=prod_data
            )
            if created:
                productos_creados += 1
                print(f"  ✅ {producto.nombre_plan}")
    
    print(f"\n  Total productos creados: {productos_creados}")
    return Producto.objects.all()


def crear_leads(productos):
    """Crea leads de ejemplo con datos de Ecuador"""
    print("\n👥 Creando leads de Ecuador...")
    
    # Obtener o crear usuario admin para asignar leads
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@callcenter.ec',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Hora actual de Ecuador
    ahora_ecuador = get_ecuador_time()
    
    leads_data = [
        # HOT LEADS
        {
            'nombre': 'Carlos',
            'apellido': 'Mendoza',
            'telefono': '+593987654321',
            'email': 'carlos.mendoza@email.com',
            'zona': 'Urdesa, Guayaquil',
            'direccion': 'Av. Víctor Emilio Estrada 123',
            'tipo_servicio_interes': TipoServicio.INTERNET,
            'presupuesto_estimado': Decimal('35.00'),
            'score': 95,
            'clasificacion': ClasificacionLead.HOT,
            'estado': EstadoLead.NEGOCIANDO,
            'fuente': FuenteLead.WHATSAPP,
            'agente_asignado': admin_user,
            'notas': 'Cliente muy interesado, quiere contratar esta semana',
            'ultima_interaccion': ahora_ecuador - timedelta(hours=2),
        },
        {
            'nombre': 'María',
            'apellido': 'Rodríguez',
            'telefono': '+593987654322',
            'email': 'maria.rodriguez@email.com',
            'zona': 'La Carolina, Quito',
            'direccion': 'Av. Amazonas y Naciones Unidas',
            'tipo_servicio_interes': TipoServicio.COMBO,
            'presupuesto_estimado': Decimal('60.00'),
            'score': 90,
            'clasificacion': ClasificacionLead.HOT,
            'estado': EstadoLead.CALIFICADO,
            'fuente': FuenteLead.LLAMADA_ENTRANTE,
            'agente_asignado': admin_user,
            'notas': 'Quiere combo completo, ya tiene fecha de instalación',
            'ultima_interaccion': ahora_ecuador - timedelta(hours=5),
        },
        
        # WARM LEADS
        {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'telefono': '+593987654323',
            'email': 'juan.perez@email.com',
            'zona': 'Kennedy Norte, Guayaquil',
            'tipo_servicio_interes': TipoServicio.MOVIL,
            'presupuesto_estimado': Decimal('20.00'),
            'score': 65,
            'clasificacion': ClasificacionLead.WARM,
            'estado': EstadoLead.CONTACTADO,
            'fuente': FuenteLead.WHATSAPP,
            'notas': 'Interesado en plan móvil, comparando precios',
            'ultima_interaccion': ahora_ecuador - timedelta(days=1),
        },
        {
            'nombre': 'Ana',
            'apellido': 'Torres',
            'telefono': '+593987654324',
            'email': 'ana.torres@email.com',
            'zona': 'El Batán, Quito',
            'tipo_servicio_interes': TipoServicio.INTERNET,
            'score': 55,
            'clasificacion': ClasificacionLead.WARM,
            'estado': EstadoLead.SEGUIMIENTO,
            'fuente': FuenteLead.WEB,
            'notas': 'Preguntó por cobertura en su zona',
            'ultima_interaccion': ahora_ecuador - timedelta(days=2),
        },
        {
            'nombre': 'Luis',
            'apellido': 'Vásquez',
            'telefono': '+593987654325',
            'email': 'luis.vasquez@email.com',
            'zona': 'Samborondón',
            'tipo_servicio_interes': TipoServicio.COMBO,
            'presupuesto_estimado': Decimal('55.00'),
            'score': 60,
            'clasificacion': ClasificacionLead.WARM,
            'estado': EstadoLead.CONTACTADO,
            'fuente': FuenteLead.WHATSAPP,
            'notas': 'Interesado en combo familiar',
            'ultima_interaccion': ahora_ecuador - timedelta(hours=18),
        },
        
        # COLD LEADS
        {
            'nombre': 'Pedro',
            'apellido': 'Sánchez',
            'telefono': '+593987654326',
            'zona': 'Alborada, Guayaquil',
            'score': 30,
            'clasificacion': ClasificacionLead.COLD,
            'estado': EstadoLead.NUEVO,
            'fuente': FuenteLead.WHATSAPP,
            'notas': 'Solo preguntó precios, no dio más información',
            'ultima_interaccion': ahora_ecuador - timedelta(days=3),
        },
        {
            'nombre': 'Laura',
            'apellido': 'Martínez',
            'telefono': '+593987654327',
            'email': 'laura.martinez@email.com',
            'zona': 'Cumbayá, Quito',
            'score': 25,
            'clasificacion': ClasificacionLead.COLD,
            'estado': EstadoLead.NUEVO,
            'fuente': FuenteLead.REDES_SOCIALES,
            'notas': 'Preguntó por promociones pero no respondió más',
            'ultima_interaccion': ahora_ecuador - timedelta(days=5),
        },
        {
            'nombre': 'Diego',
            'apellido': 'Flores',
            'telefono': '+593987654328',
            'zona': 'Cuenca Centro',
            'score': 20,
            'clasificacion': ClasificacionLead.COLD,
            'estado': EstadoLead.NUEVO,
            'fuente': FuenteLead.WEB,
            'notas': 'Visitó la página web, no dejó más datos',
            'ultima_interaccion': ahora_ecuador - timedelta(days=7),
        },
    ]
    
    leads = []
    for lead_data in leads_data:
        # Asignar producto de interés si tiene tipo de servicio
        if 'tipo_servicio_interes' in lead_data and lead_data['tipo_servicio_interes']:
            producto = productos.filter(
                tipo=lead_data['tipo_servicio_interes'],
                is_destacado=True
            ).first()
            if producto:
                lead_data['producto_interes'] = producto
                lead_data['operador_interes'] = producto.operador
        
        lead, created = Lead.objects.get_or_create(
            telefono=lead_data['telefono'],
            defaults=lead_data
        )
        leads.append(lead)
        if created:
            print(f"  ✅ {lead.nombre_completo} - {lead.get_clasificacion_display()} - {lead.zona}")
        else:
            print(f"  ℹ️  Ya existe: {lead.nombre_completo}")
    
    return leads


def crear_conversaciones(leads):
    """Crea conversaciones de ejemplo con contexto ecuatoriano"""
    print("\n💬 Creando conversaciones...")
    
    ahora_ecuador = get_ecuador_time()
    
    conversaciones_data = [
        # Conversación de Carlos (HOT)
        {
            'lead': leads[0],  # Carlos
            'canal': CanalConversacion.WHATSAPP,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Hola, quiero contratar internet de 50 megas para mi casa en Urdesa',
            'respuesta_sistema': '¡Hola Carlos! 👋 Excelente elección. Tenemos el plan perfecto para Urdesa. El plan de 50 Mbps está en promoción a $29.75/mes. ¿Te interesa?',
            'sentimiento': SentimientoConversacion.POSITIVO,
            'fue_atendido_por_ia': True,
            'intenciones_detectadas': ['INTERES_COMPRA', 'CONSULTA_TECNICA', 'CONSULTA_DISPONIBILIDAD'],
        },
        {
            'lead': leads[0],  # Carlos - Segunda conversación
            'canal': CanalConversacion.WHATSAPP,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Sí me interesa! Cuándo pueden instalar?',
            'respuesta_sistema': 'Perfecto! Podemos agendar la instalación para esta semana. ¿Qué día te viene mejor? Tenemos disponibilidad de lunes a sábado.',
            'sentimiento': SentimientoConversacion.POSITIVO,
            'fue_atendido_por_ia': True,
            'intenciones_detectadas': ['INTERES_COMPRA', 'SOLICITUD_CONTACTO'],
        },
        
        # Conversación de María (HOT)
        {
            'lead': leads[1],  # María
            'canal': CanalConversacion.LLAMADA,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Buenos días, quiero información sobre paquetes combo en La Carolina',
            'respuesta_sistema': 'Buenos días María! Con gusto. Para La Carolina tenemos el Combo Familiar a $44/mes con Internet 50 Mbps + TV + Teléfono.',
            'transcripcion': 'Cliente llamó desde Quito preguntando por combos. Muy interesada en el combo total.',
            'duracion_segundos': 180,
            'sentimiento': SentimientoConversacion.POSITIVO,
            'fue_atendido_por_ia': False,
            'intenciones_detectadas': ['INTERES_COMPRA', 'CONSULTA_PRECIO', 'CONSULTA_DISPONIBILIDAD'],
        },
        
        # Conversación de Juan (WARM)
        {
            'lead': leads[2],  # Juan
            'canal': CanalConversacion.WHATSAPP,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Hola, cuánto cuesta el plan de 10GB?',
            'respuesta_sistema': 'Hola Juan! El plan de 10GB está en $18/mes con descuento. Incluye 500 minutos y redes sociales ilimitadas. Cobertura en todo Ecuador.',
            'sentimiento': SentimientoConversacion.NEUTRAL,
            'fue_atendido_por_ia': True,
            'intenciones_detectadas': ['CONSULTA_PRECIO'],
        },
        
        # Conversación de Luis (WARM)
        {
            'lead': leads[4],  # Luis
            'canal': CanalConversacion.WHATSAPP,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Tienen cobertura en Samborondón? Necesito internet y TV',
            'respuesta_sistema': '¡Sí Luis! Tenemos excelente cobertura en Samborondón. El Combo Familiar incluye Internet 50 Mbps + 80 canales de TV a $44/mes. ¿Te interesa?',
            'sentimiento': SentimientoConversacion.POSITIVO,
            'fue_atendido_por_ia': True,
            'intenciones_detectadas': ['CONSULTA_DISPONIBILIDAD', 'INTERES_COMPRA'],
        },
        
        # Conversación de Pedro (COLD)
        {
            'lead': leads[5],  # Pedro
            'canal': CanalConversacion.WHATSAPP,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Precios de internet?',
            'respuesta_sistema': 'Hola! Tenemos planes desde $22.50/mes (20 Mbps) hasta $40/mes (100 Mbps). ¿En qué zona de Guayaquil vives?',
            'sentimiento': SentimientoConversacion.NEUTRAL,
            'fue_atendido_por_ia': True,
            'intenciones_detectadas': ['CONSULTA_PRECIO'],
        },
    ]
    
    conversaciones_creadas = 0
    for conv_data in conversaciones_data:
        conversacion = Conversacion.objects.create(**conv_data)
        conversaciones_creadas += 1
        print(f"  ✅ Conversación con {conversacion.lead.nombre_completo} - {conversacion.get_canal_display()}")
    
    print(f"\n  Total conversaciones creadas: {conversaciones_creadas}")


def crear_ventas(leads, productos):
    """Crea ventas de ejemplo"""
    print("\n💰 Creando ventas...")
    
    admin_user = User.objects.get(username='admin')
    ahora_ecuador = get_ecuador_time()
    
    ventas_data = [
        {
            'lead': leads[0],  # Carlos
            'producto': productos.filter(nombre_plan__contains='50 Mbps', tipo=TipoServicio.INTERNET).first(),
            'agente': admin_user,
            'fue_venta_ia': False,
            'precio_final': Decimal('29.75'),
            'descuento_aplicado': Decimal('5.25'),
            'comision_agente': Decimal('35.00'),
            'fecha_instalacion': (ahora_ecuador + timedelta(days=3)).date(),
            'direccion_instalacion': 'Av. Víctor Emilio Estrada 123, Urdesa, Guayaquil',
            'estado': EstadoVenta.PENDIENTE,
            'notas': 'Cliente confirmó instalación para el viernes',
        },
    ]
    
    ventas_creadas = 0
    for venta_data in ventas_data:
        if venta_data['producto']:
            venta = Venta.objects.create(**venta_data)
            ventas_creadas += 1
            print(f"  ✅ Venta a {venta.lead.nombre_completo} - ${venta.precio_final}")
    
    print(f"\n  Total ventas creadas: {ventas_creadas}")


def main():
    """Función principal"""
    ahora_ecuador = get_ecuador_time()
    
    print("=" * 80)
    print("🇪🇨 POBLANDO BASE DE DATOS - CALL CENTER IA ECUADOR")
    print("=" * 80)
    print(f"📅 Fecha y hora Ecuador: {ahora_ecuador.strftime('%d/%m/%Y %H:%M:%S %Z')}")
    print(f"🌍 Zona horaria: America/Guayaquil (GMT-5)")
    print("=" * 80)
    
    try:
        # Crear datos
        operadores = crear_operadores()
        productos = crear_productos(operadores)
        leads = crear_leads(productos)
        crear_conversaciones(leads)
        crear_ventas(leads, productos)
        
        # Resumen
        print("\n" + "=" * 80)
        print("✅ DATOS CREADOS EXITOSAMENTE PARA ECUADOR")
        print("=" * 80)
        print(f"📱 Operadores: {Operador.objects.count()}")
        print(f"   • Claro Ecuador")
        print(f"   • Movistar Ecuador")
        print(f"   • CNT")
        print(f"   • Tuenti Ecuador")
        print(f"\n📦 Productos: {Producto.objects.count()}")
        print(f"👥 Leads: {Lead.objects.count()}")
        print(f"   🔥 HOT: {Lead.objects.filter(clasificacion='HOT').count()}")
        print(f"   🌡️  WARM: {Lead.objects.filter(clasificacion='WARM').count()}")
        print(f"   ❄️  COLD: {Lead.objects.filter(clasificacion='COLD').count()}")
        print(f"💬 Conversaciones: {Conversacion.objects.count()}")
        print(f"💰 Ventas: {Venta.objects.count()}")
        print("=" * 80)
        print("\n🎉 ¡Listo! Ahora puedes acceder al admin:")
        print("   http://localhost:8000/admin/")
        print("\n   Usuario: admin")
        print("   Contraseña: admin123 (si usaste create_superuser.py)")
        print("\n🇪🇨 Datos configurados para Ecuador - Guayaquil")
        print(f"   Hora actual: {ahora_ecuador.strftime('%H:%M:%S')}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
